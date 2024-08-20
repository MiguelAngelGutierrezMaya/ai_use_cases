from PIL import Image
from transformers import pipeline


class ProcessImage:
    def __init__(self, image_path: str):
        self.image_path = image_path

    def process(self):
        pipe = pipeline("image-classification", model="Falconsai/nsfw_image_detection")
        image = Image.open(self.image_path)
        return pipe(image)
