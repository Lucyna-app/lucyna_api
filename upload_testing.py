from pathlib import Path
import requests
import uuid
import sys


#                                                  Toggle this guy to run for real ⤵
def send_upload_post_request(
    char_name: str,
    series_uuid4: str,
    series_name: str,
    art_path: Path,
    rarity: int,
    dry_run: bool = False,
):
    # Define the payload of text arguments in the form
    data = {
        "character_name": char_name[:-4],
        "series_uuid4": series_uuid4,
        "series_name": series_name,
        "rarity": rarity,
    }

    # attach the image
    files = {"art": ("character.png", art_path.read_bytes(), "image/png")}

    if not dry_run:
        # Send the POST request
        response = requests.post(
            "http://127.0.0.1:8000/create_complete_character", data=data, files=files
        )

        # Print the response status code and text
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

    else:
        print(
            f"character_name: {char_name[:-4]} | series_uuid4:{series_uuid4} | art_path: {art_path} | rarity: {rarity}"
        )


def upload_series_directory(folder_path: Path):
    """
    Given a path to a series folder full of PNGs, upload them all to an API endpoint with rarity 1
    """
    assert folder_path.is_dir()

    tmp_series_name = str(folder_path.name)
    data = {"series_name": tmp_series_name}
    response = requests.post("http://127.0.0.1:8000/series/create", data=data)

    for png_file in folder_path.rglob("*.png"):
        series_uuid4 = response.json()["message"]
        char_name = str(png_file.name)
        rarity = 1
        send_upload_post_request(
            char_name, series_uuid4, tmp_series_name, png_file, rarity
        )


def bulk_upload(folder_path: Path):
    """ """
    assert folder_path.is_dir()

    for child_elem in folder_path.iterdir():
        if child_elem.is_dir():
            upload_series_directory(child_elem)


if __name__ == "__main__":
    userin_path = Path(sys.argv[1])
    bulk_upload(userin_path)
