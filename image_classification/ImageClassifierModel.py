from torch import nn
from torchvision.models import resnet152


class ImageClassifierModel(nn.Module):
    def __init__(self, num_classes=4):
        super(ImageClassifierModel, self).__init__()
        self.num_classes = num_classes
        self.features = resnet152(weights=weights)

        in_features = self.features.fc.in_features
        self.features.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        x = self.features(x)
        return x
