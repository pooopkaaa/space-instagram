import argparse
from pathlib import Path
from urllib.parse import urljoin

import requests
import urllib3

from handler import download_image, get_file_extension_from_url, get_response


def get_command_line_args():
    parser = argparse.ArgumentParser(description='Загрузка изображений опубликованных\
                                     с телескопа Hubble с помощью предоставленного API.\
                                     Укажите коллекцию изображений, которые необходимо загрузить.\
                                     Дополнительно можно загрузить изображение по заданному id.')
    parser.add_argument('-f',
                        '--folder',
                        default='images/',
                        help='Укажите в какую папку загрузить изображения.')
    parser.add_argument('-c',
                        '--collection',
                        help='Укажите какую коллекцию изображений загрузить.')
    parser.add_argument('-i',
                        '--id',
                        help='Укажите какой id изображения загрузить.')
    return parser.parse_args()


def fetch_hubble_from_collection(collection_name, folder):
    url = f'http://hubblesite.org/api/v3/images/{collection_name}'
    response = get_response(url)
    image_ids = [image_element['id'] for image_element in response.json()]
    for image_id in image_ids:
        fetch_hubble_from_id(image_id, folder)


def fetch_hubble_from_id(image_id, folder):
    url = f'http://hubblesite.org/api/v3/image/{image_id}'
    response = get_response(url)
    non_scheme_image_url = response.json()['image_files'][-1]['file_url']
    image_url = urljoin('https://', non_scheme_image_url)
    image_title = f'hubble{image_id}{get_file_extension_from_url(image_url)}'
    download_image(image_url, image_title, folder)


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    command_line_args = get_command_line_args()
    images_folder = command_line_args.folder
    Path(images_folder).mkdir(exist_ok=True)
    hubble_collection_name = command_line_args.collection
    hubble_image_id = command_line_args.id

    try:
        if hubble_collection_name:
            fetch_hubble_from_collection(hubble_collection_name, images_folder)
        if hubble_image_id:
            fetch_hubble_from_id(hubble_image_id, images_folder)
    except requests.exceptions.HTTPError as request_error:
        exit(f'Не могу получить ответ от сервера -> {request_error}')


if __name__ == '__main__':
    main()
