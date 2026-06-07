from functools import lru_cache
import base64
from io import BytesIO

import numpy as np
import torch
from PIL import Image
from torchvision import models, transforms

from medassist_lung_agent.config import settings


CLASS_NAMES = ["normal", "pneumonia"]


def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=1)
def load_chest_model():
    if not settings.chest_model_path.exists():
        raise FileNotFoundError(f"Chest model not found: {settings.chest_model_path}")

    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(512, 2)
    state = torch.load(settings.chest_model_path, map_location=_device())
    model.load_state_dict(state)
    model.to(_device())
    model.eval()
    return model


def _preprocess(image: Image.Image) -> torch.Tensor:
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    return transform(image).unsqueeze(0).to(_device())


def _png_base64(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _colorize_heatmap(cam: np.ndarray) -> np.ndarray:
    cam = np.clip(cam, 0, 1)
    red = np.clip(1.5 * cam, 0, 1)
    green = np.clip(1.5 * (1 - np.abs(cam - 0.55) * 2), 0, 1)
    blue = np.clip(1.4 * (1 - cam), 0, 1)
    return np.stack([red, green, blue], axis=-1)


def _make_gradcam(model, image_tensor: torch.Tensor, class_idx: int, original: Image.Image) -> str:
    activations = []
    gradients = []

    def forward_hook(_, __, output):
        activations.append(output.detach())

    def backward_hook(_, __, grad_output):
        gradients.append(grad_output[0].detach())

    target_layer = model.layer4[-1]
    handle_fwd = target_layer.register_forward_hook(forward_hook)
    handle_bwd = target_layer.register_full_backward_hook(backward_hook)
    try:
        model.zero_grad(set_to_none=True)
        logits = model(image_tensor)
        logits[0, class_idx].backward()
    finally:
        handle_fwd.remove()
        handle_bwd.remove()

    if not activations or not gradients:
        return ""

    acts = activations[0][0]
    grads = gradients[0][0]
    weights = grads.mean(dim=(1, 2), keepdim=True)
    cam = torch.relu((weights * acts).sum(dim=0))
    cam = cam.detach().cpu().numpy()
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

    heat = Image.fromarray(np.uint8(cam * 255)).resize(original.size, Image.Resampling.BILINEAR)
    heat_arr = np.asarray(heat, dtype=np.float32) / 255.0
    color = _colorize_heatmap(heat_arr)
    base = np.asarray(original.convert("RGB"), dtype=np.float32) / 255.0
    overlay = np.clip(base * 0.58 + color * 0.42, 0, 1)
    return _png_base64(Image.fromarray(np.uint8(overlay * 255)))


def analyze_xray_bytes(image_bytes: bytes, filename: str = "upload") -> dict:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    model = load_chest_model()
    tensor = _preprocess(image)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).detach().cpu().numpy()[0]

    scores = {name: float(prob) for name, prob in zip(CLASS_NAMES, probs)}
    pred = max(scores, key=scores.get)
    class_idx = CLASS_NAMES.index(pred)
    gradcam = _make_gradcam(model, tensor, class_idx, image)
    risk_note = (
        "模型提示肺炎概率较高，请结合症状、体征、血常规/炎症指标和医生阅片进一步确认。"
        if pred == "pneumonia"
        else "模型未提示明显肺炎特征，但若有发热、咳嗽、胸痛或呼吸困难仍需就医评估。"
    )
    return {
        "filename": filename,
        "prediction": pred,
        "scores": scores,
        "gradcam_png_base64": gradcam,
        "risk_note": risk_note,
        "medical_disclaimer": "AI 结果仅供辅助参考，不能替代放射科医生或临床医生诊断。",
    }
