from torch import nn
from torchvision.models import resnet50, ResNet50_Weights


class ImageClassifierModel(nn.Module):
    def __init__(self, num_classes=53):
        super(ImageClassifierModel, self).__init__()
        self.num_classes = num_classes
        self.weights = ResNet50_Weights.DEFAULT
        self.features = resnet50(weights=self.weights)

        in_features = self.features.fc.in_features
        self.features.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        x = self.features(x)
        return x