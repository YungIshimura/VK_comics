import requests
import os
import urllib
import random
from dotenv import load_dotenv


def check_answer(response):
    if 'error' in response:
        raise Exception(
            response['error']['error_code'],
            response['error']['error_msg']
        )


def get_file_extension(url):
    url = urllib.parse.unquote(url)
    url_split = urllib.parse.urlsplit(url)
    path = url_split[2]

    return os.path.splitext(path)[1]


def get_number_of_comics():
    response = requests.get("https://xkcd.com/info.0.json")
    response.raise_for_status()
    xkcd_response = response.json()
    number = xkcd_response['num']
    image_url = xkcd_response['img']

    return number, image_url


def get_random_comic(number):
    comic_number = random.randint(1, number)
    url = f"https://xkcd.com/{comic_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()
    image_link = comic["img"]
    comment = comic["alt"]

    return image_link, comment


def download_image(image_link, extension, filename):
    response = requests.get(image_link)
    response.raise_for_status()
    with open(f"{filename}{extension}", "wb") as file:
        file.write(response.content)


def get_photo_upload_addresses(token, group_id):
    params = {
        "access_token": token,
        "v": "5.131.",
        "group_id": group_id
    }
    response = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer", params=params)
    response.raise_for_status()
    upload_addresses = response.json()
    check_answer(upload_addresses)

    return upload_addresses['response']['upload_url']


def deploy_photo(upload_adress):
    with open(f"{filename}{extension}", "rb") as file:
        files = {
            "photo": file
        }
        response = requests.post(upload_adress, files=files)
    response.raise_for_status()
    response = response.json()
    check_answer(response)

    return response['server'], response['photo'], response['hash']


def save_photo_album(token, group_id, photo, server, photo_hash):
    params = {
        "access_token": token,
        "v": "5.131.",
        "group_id": group_id,
        "photo": photo,
        "server": server,
        "hash": photo_hash
    }
    response = requests.post(
        "https://api.vk.com/method/photos.saveWallPhoto", params=params)
    response.raise_for_status()
    server_response = response.json()
    photo_id = server_response['response'][0]['id']
    check_answer(server_response)

    return photo_id


def publication_comics_on_the_wall(
        token, group_id, user_id, media_id, comment):
    params = {
        "access_token": token,
        "v": "5.131.",
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "attachments": f"photo{user_id}_{media_id}",
        "message": comment
    }
    response = requests.post(
        "https://api.vk.com/method/wall.post", params=params)
    response.raise_for_status()
    answer = response.json()
    check_answer(answer)


if __name__ == "__main__":
    load_dotenv()
    vk_group_id = os.getenv("GROUP_ID")
    vk_api_key = os.getenv("VK_API_KEY")
    vk_user_id = os.getenv("USER_ID")
    try:
        filename = "image"
        number, image_url = get_number_of_comics()
        extension = get_file_extension(image_url)
        image_link, comment = get_random_comic(number)
        download_image(image_link, extension, filename)
        upload_adress = get_photo_upload_addresses(vk_api_key, vk_group_id)
        server, photo, photo_hash = deploy_photo(upload_adress)
        media_id = save_photo_album(
            vk_api_key, vk_group_id, photo, server, photo_hash)
        publication_comics_on_the_wall(
            vk_api_key, vk_group_id, vk_user_id, media_id, comment)
    finally:
        os.remove(f"{filename}{extension}")
