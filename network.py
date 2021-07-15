import torch
from torchvision import transforms


class Classify(object):
    __slots__ = ["device", "dtype", "network", "preprocess"]

    def __init__(self, tuned_weights=None):
        self.device = torch.device("cuda")
        self.dtype = torch.float32
        if not tuned_weights:
            self.network = torch.hub.load(
                "pytorch/vision:v0.9.0", "resnet152", pretrained=True
            )
        else:
            self.network = torch.hub.load(
                "pytorch/vision:v0.9.0", "resnet152", pretrained=False
            )
            self.network.load_state_dict(tuned_weights["model_state_dict"])
        self.network = self.network.to(self.device)
        self.network = torch.jit.script(self.network)
        self.network.eval()
        self.preprocess = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    @torch.no_grad()
    def __call__(self, pil_image):
        input_tensor = self.preprocess(pil_image).to(
            dtype=self.dtype, device=self.device
        )
        outputs = self.network(input_tensor.unsqueeze(0)).cpu()
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        _, top5 = torch.topk(probs, 5)
        return top5
