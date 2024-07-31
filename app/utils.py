import uuid
from PIL import Image

def gen_uuid4():
    return str(uuid.uuid4())

def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image
    except IOError:
        print(f"Unable to load image:  {image_path}")
        return None