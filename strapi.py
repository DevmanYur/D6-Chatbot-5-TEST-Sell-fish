import os
from pprint import pprint
import requests
from dotenv import load_dotenv

load_dotenv()

strapi_token = os.getenv("STRAPI_TOKEN")
headers = {'Authorization': f'Bearer {strapi_token}'}
response0 = requests.get(f'http://localhost:1337/api/products/vf9v1zcox2ugiha5zkaqgnm7?populate=picture',headers=headers)
product = response0.json()

url_pic = product['data']['picture']['url']


name_photo = 'ddd2'
photo_format = 'jpeg'
response = requests.get(f'http://localhost:1337{url_pic}')
response.raise_for_status()

photo_path = f'{name_photo}.{photo_format}'
with open(photo_path, 'wb') as file:
    file.write(response.content)











import io
from io import BytesIO
from pprint import pprint

import requests






# with open(filename, 'wb') as file:
#     file.write(response.content)