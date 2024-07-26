from pathlib import Path
import requests


#                                                  Toggle this guy to run for real ⤵
def send_upload_post_request(
    char_name: str, series_name: str, art_path: Path, rarity: int, dry_run: bool = False
):
    # Define the payload of text arguments in the form
    data = {
        "character_name": char_name[:-4],
        "series_name": series_name,
        "rarity": rarity,
    }

    # attach the image
    files = {"art": ("character.png", art_path.read_bytes(), "image/png")}

    if not dry_run:
        # Send the POST request
        response = requests.post(
            "http://127.0.0.1:8000/upload/character", data=data, files=files
        )

        # Print the response status code and text
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

    else:
        print(
            f"character_name: {char_name[:-4]} | series_name:{series_name} | art_path: {art_path} | rarity: {rarity}"
        )


def upload_series_directory(folder_path: Path):
    """
    Given a path to a series folder full of PNGs, upload them all to an API endpoint with rarity 1
    """
    assert folder_path.is_dir()
    for png_file in folder_path.rglob("*.png"):
        series_name = str(folder_path.name)
        char_name = str(png_file.name)
        rarity = 1
        send_upload_post_request(char_name, series_name, png_file, rarity)


if __name__ == "__main__":
    userin_path = Path(input("Paste absolute path to series folder here: "))
    upload_series_directory(userin_path)
