
import os
import torch
import tqdm
from dotenv import load_dotenv
from torch import nn
from torch.utils.data import DataLoader
from torchvision.models import ResNet50_Weights

from ImageClassifierDataset import ImageClassifierDataset
from ImageClassifierModel import ImageClassifierModel

# ---- setup ----
weights = ResNet50_Weights.DEFAULT
transforms = weights.transforms()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
AMP_ENABLED = (device.type == "cuda")


def build_loaders(datafolder: str, batch_size: int = 64):
    train_folder = os.path.join(datafolder, "train")
    valid_folder = os.path.join(datafolder, "valid")

    train_dataset = ImageClassifierDataset(train_folder, transform=transforms)
    val_dataset = ImageClassifierDataset(valid_folder, transform=transforms)

    # DataLoader perf knobs
    num_workers = min(8, os.cpu_count() or 2)
    pin = (device.type == "cuda")

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin,
        persistent_workers=(num_workers > 0),
        prefetch_factor=2 if num_workers > 0 else None,
        drop_last=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin,
        persistent_workers=(num_workers > 0),
        prefetch_factor=2 if num_workers > 0 else None,
        drop_last=False,
    )
    return train_dataset, val_dataset, train_loader, val_loader


@torch.no_grad()
def evaluate_model(model, data_loader, criterion=None):
    model.eval()
    total, correct = 0, 0
    loss_sum = 0.0

    for images, labels in data_loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        outputs = model(images)
        if criterion is not None:
            loss_sum += criterion(outputs, labels).item() * labels.size(0)

        preds = outputs.argmax(dim=1)
        total += labels.size(0)
        correct += (preds == labels).sum().item()

    acc = 100.0 * correct / max(total, 1)
    avg_loss = loss_sum / max(total, 1) if criterion is not None else None
    return acc, avg_loss


def save_model(model, class_names, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "class_names": class_names,
        },
        path,
    )


def load_model(path):
    checkpoint = torch.load(path, map_location=device)
    class_names = checkpoint["class_names"]
    model = ImageClassifierModel(num_classes=len(class_names))
    model.load_state_dict(checkpoint["model_state"])
    model.to(device).eval()
    return model, class_names


def train_model(
    datafolder,
    num_epochs=10,
    learning_rate=1e-3,
    batch_size=64,
    num_classes=53,
    model_path="models/classifier_best.pth",
    label_smoothing=0.0,
):
    train_dataset, val_dataset, train_loader, val_loader = build_loaders(datafolder, batch_size)

    model = ImageClassifierModel(num_classes=num_classes).to(device)

    # Optional speed on Ampere+ GPUs
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        try:
            torch.set_float32_matmul_precision("high")  # PyTorch 2.x
        except Exception:
            pass

    criterion = nn.CrossEntropyLoss(label_smoothing=label_smoothing)

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=learning_rate,
        momentum=0.9,
        weight_decay=1e-4,
        nesterov=True,
    )

    # Better schedule for classification than ReduceLROnPlateau in many cases
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    scaler = torch.amp.GradScaler('cuda', enabled=AMP_ENABLED)

    best_val_acc = -1.0
    history = {"train_loss": [], "val_loss": [], "val_acc": []}

    for epoch in range(1, num_epochs + 1):
        model.train()
        running_loss = 0.0
        seen = 0

        pbar = tqdm.tqdm(train_loader, desc=f"Epoch {epoch}/{num_epochs} [train]", leave=False)
        for images, labels in pbar:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast('cuda',enabled=AMP_ENABLED):
                outputs = model(images)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            bs = labels.size(0)
            running_loss += loss.item() * bs
            seen += bs
            pbar.set_postfix(loss=running_loss / max(seen, 1))

        train_loss = running_loss / max(seen, 1)

        val_acc, val_loss = evaluate_model(model, val_loader, criterion=criterion)

        scheduler.step()

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        # Save only best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_model(model, train_dataset.classes, model_path)

        print(
            f"Epoch {epoch}/{num_epochs} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | val_acc={val_acc:.2f}% | "
            f"best={best_val_acc:.2f}%"
        )

    return history


def predict(input_image, model_weights_path, topk=4):
    model, class_names = load_model(model_weights_path)

    with torch.no_grad():
        x = transforms(input_image).unsqueeze(0).to(device)
        logits = model(x)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        top_probs, top_idxs = torch.topk(probs, k=topk)

    return [(class_names[i], float(p)) for i, p in zip(top_idxs.tolist(), top_probs.tolist())]

if __name__ == "__main__":
    # Example usage: train the model
    load_dotenv()
    data_folder = os.getenv("DATA_FOLDER", "./data")
    train_model(
        datafolder=data_folder,
        num_epochs=5,
        learning_rate=0.01,
        batch_size=32,
        num_classes=53,
        model_path="models/classifier_best.pth",
        label_smoothing=0.1,
    )
