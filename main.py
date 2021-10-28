import requests
import os
import urllib
import random
from dotenv import load_dotenv


def get_file_extension(url):
    url = urllib.parse.unquote(url)
    url_split = urllib.parse.urlsplit(url)
    path = url_split[2]

    return os.path.splitext(path)[1]


def get_number_of_comics():
    response = requests.get("https://xkcd.com/info.0.json")
    xkcd_response = response.json()
    number = xkcd_response['num']
    image_url = xkcd_response['img']

    return number, image_url


def get_image_link_and_comment(number):
    comic_number = random.randint(1, number)
    url = f"https://xkcd.com/{comic_number}/info.0.json"
    response = requests.get(url)
    comic = response.json()
    image_link = comic["img"]
    comment = comic["alt"]

    return image_link, comment


def download_image(image_link):
    response = requests.get(image_link)
    with open(f"{filename}{extension}", "wb") as file:
        file.write(response.content)


def get_photo_upload_addresses(token):
    params = {
        "access_token": token,
        "v": "5.131.",
        "group_id": "207920447"
    }
    response = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer", params=params)
    response.raise_for_status()
    upload_addresses = response.json()
    for upload_adress in upload_addresses.values():
        return upload_adress["upload_url"]


def deploy_photo(upload_adress):
    server_data = []
    with open(f"{filename}{extension}", "rb") as file:
        files = {
            "photo": file
        }
        response = requests.post(upload_adress, files=files)
        response.raise_for_status()
        server_callback = response.json()
        for media in server_callback.values():
            server_data.append(media)

    return server_data


def save_photo_album(token, photo, server, hash):
    params = {
        "access_token": token,
        "v": "5.131.",
        "group_id": group_id,
        "photo": photo,
        "server": server,
        "hash": hash
    }
    response = requests.post(
        "https://api.vk.com/method/photos.saveWallPhoto", params=params)
    server_response = response.json()
    for photo_identifiers in server_response.values():
        for media in photo_identifiers:
            id = media["id"]

    return id


def publication_comics_on_the_wall(
        token, group_id, user_id, media_id, comment):
    params = {
        "access_token": token,
        "v": "5.131.",
        "owner_id": f"-{int(group_id)}",
        "from_group": 1,
        "attachments": f"photo{user_id}_{media_id}",
        "message": comment
    }
    requests.post("https://api.vk.com/method/wall.post", params=params)


if __name__ == "__main__":
    load_dotenv()
    group_id = os.getenv("GROUP_ID")
    vk_api_key = os.getenv("VK_API_KEY")
    user_id = os.getenv("USER_ID")
    filename = input("Введите название файла ")
    number, image_url = get_number_of_comics()
    extension = get_file_extension(image_url)
    image_link, comment = get_image_link_and_comment(number)
    download_image(image_link)
    upload_adress = get_photo_upload_addresses(vk_api_key)
    server_data = deploy_photo(upload_adress,)
    server, photo, hash = server_data
    media_id = save_photo_album(vk_api_key, photo, server, hash)
    publication_comics_on_the_wall(
        vk_api_key, group_id, user_id, media_id, comment)
    os.remove(f"{filename}{extension}")
