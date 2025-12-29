from torch import nn
from torchvision.models import resnet152, ResNet152_Weights


class ImageClassifierModel(nn.Module):
    def __init__(self, num_classes=6):
        super(ImageClassifierModel, self).__init__()
        self.num_classes = num_classes
        self.weights = ResNet152_Weights.DEFAULT
        self.features = resnet152(weights=self.weights)

        in_features = self.features.fc.in_features
        self.features.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        x = self.features(x)
        return x