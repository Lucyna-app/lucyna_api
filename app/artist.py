from PIL import Image, ImageDraw, ImageFont
import io
import os

FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dystopian.otf")


def draw_text_on_image(
    image: Image.Image, character_name: str, series_name: str
) -> Image.Image:
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 20)

    draw.text((10, 10), series_name, font=font, fill=(255, 255, 255))

    text_width = draw.textlength(character_name, font=font)
    draw.text(
        (image.width - text_width - 10, image.height - 30),
        character_name,
        font=font,
        fill=(255, 255, 255),
    )

    return image


def combine_images(images: list[Image.Image]) -> bytes:
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    combined_image = Image.new("RGB", (total_width, max_height))
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()
