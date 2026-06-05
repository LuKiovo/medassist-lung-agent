from functools import lru_cache
from io import BytesIO

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


def analyze_xray_bytes(image_bytes: bytes, filename: str = "upload") -> dict:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    model = load_chest_model()

    with torch.no_grad():
        logits = model(_preprocess(image))
        probs = torch.softmax(logits, dim=1).detach().cpu().numpy()[0]

    scores = {name: float(prob) for name, prob in zip(CLASS_NAMES, probs)}
    pred = max(scores, key=scores.get)
    risk_note = (
        "模型提示肺炎概率较高，请结合症状、体征、血常规/炎症指标和医生阅片进一步确认。"
        if pred == "pneumonia"
        else "模型未提示明显肺炎特征，但若有发热、咳嗽、胸痛或呼吸困难仍需就医评估。"
    )
    return {
        "filename": filename,
        "prediction": pred,
        "scores": scores,
        "risk_note": risk_note,
        "medical_disclaimer": "AI 结果仅供辅助参考，不能替代放射科医生或临床医生诊断。",
    }

