from PIL import Image, ImageDraw, ImageFont
from .utils import load_image
import io
import os

FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/cinzel_regular.otf"
)
BORDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/base_border.png"
)
RARITY_1_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/rarity_1.png"
)
RARITY_2_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/rarity_2.png"
)
RARITY_3_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/rarity_3.png"
)
RARITY_4_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/rarity_4.png"
)
RARITY_5_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "assets/rarity_5.png"
)


def draw_text_on_image(
    image: Image.Image, character_name: str, series_name: str, rarity: int
) -> Image.Image:
    border_image = load_image(BORDER_PATH)
    image.paste(border_image, (0, 0), border_image)

    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 30)

    # Calculate text width
    bbox = draw.textbbox((0, 0), character_name, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (image.width - text_width) // 2
    text_y = image.height - 52

    draw.text((text_x, text_y), character_name, font=font, fill=(255, 251, 203))

    symbol_size = (30, 30)  # Adjust as needed
    rarity_symbol = load_image(RARITY_5_PATH)
    rarity_position = (image.width // 2 - symbol_size[0] // 2 - 6, image.height - 85)
    image.paste(rarity_symbol, rarity_position, rarity_symbol)

    return image


def combine_images(images: list[Image.Image]) -> bytes:
    padding = 10
    total_width = sum(img.width for img in images) + padding * (len(images) - 1)
    max_height = max(img.height for img in images)

    combined_image = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))
    x_offset = 0
    for img in images:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        combined_image.paste(img, (x_offset, 0), img)
        x_offset += img.width + padding

    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()
