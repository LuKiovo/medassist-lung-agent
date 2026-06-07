import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from medassist_lung_agent.imaging.chest_xray import CLASS_NAMES, load_chest_model


def build_loader(data_dir: Path, batch_size: int, num_workers: int):
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.Grayscale(num_output_channels=3),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    dataset = datasets.ImageFolder(str(data_dir), transform=transform)
    return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers), dataset


def main():
    parser = argparse.ArgumentParser(description="Evaluate the chest X-ray CNN on an ImageFolder dataset.")
    parser.add_argument("--data-dir", required=True, help="Path to test folder with NORMAL/PNEUMONIA subfolders")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--output", default="data/cnn_eval.json")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loader, dataset = build_loader(Path(args.data_dir), args.batch_size, args.num_workers)
    model = load_chest_model()

    y_true: list[int] = []
    y_pred: list[int] = []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            logits = model(images)
            pred = logits.argmax(dim=1).cpu().tolist()
            y_pred.extend(pred)
            y_true.extend(labels.tolist())

    labels = list(range(len(dataset.classes)))
    report = classification_report(y_true, y_pred, labels=labels, target_names=dataset.classes, output_dict=True)
    result = {
        "classes": dataset.classes,
        "expected_class_order": CLASS_NAMES,
        "accuracy": accuracy_score(y_true, y_pred),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "classification_report": report,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
