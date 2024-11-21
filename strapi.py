import os
from pprint import pprint
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
load_dotenv()


def f1():
    ####555
    strapi_tokenq55 = os.getenv("STRAPI_TOKEN")
    headersq55 = {'Authorization': f'Bearer {strapi_tokenq55}'}
    response055 = requests.get(f'http://localhost:1337/api/products/zn17dtr0wv00kq32i0y8b3n1?populate=picture',headers=headersq55)
    productq55 = response055.json()

    url_picq55 = productq55['data']['picture']['formats']['thumbnail']['url']

    name_photo55 = productq55['data']['picture']['formats']['thumbnail']['name']
    # name_photo = 'ddqq'
    response2255 = requests.get(f'http://localhost:1337{url_picq55}')
    response2255.raise_for_status()

    image_data2255 = BytesIO(response2255.content)
    img55 = Image.open(image_data2255)
    ####555
    img55.save('img3.png')


def f2():
    x = 'POST http://localhost:1337/api/restaurants'

    strapi_tokenq66 = os.getenv("STRAPI_TOKEN")
    headersq66 = {'Authorization': f'Bearer {strapi_tokenq66}'}
    response066 = requests.get(f'http://localhost:1337/api/carts',headers=headersq66)
    productq66 = response066.json()
    pprint(productq66)

def f3():
    strapi_tokenq66 = os.getenv("STRAPI_TOKEN")
    headersq66 = {'Authorization': f'Bearer {strapi_tokenq66}'}

    data = {'data': {'tg_id': '510011'}}

    response066 = requests.post(f'http://localhost:1337/api/carts', headers=headersq66, json = data)
    productq66 = response066.json()
    pprint(productq66)

'''
{'data': [{'createdAt': '2024-11-21T13:29:51.740Z',
           'documentId': 'yyl0wssrpdz3oku2xidfnof9',
           'id': 2,
           'publishedAt': '2024-11-21T13:29:52.839Z',
           'tg_id': '1001',
           'updatedAt': '2024-11-21T13:29:52.823Z'}}
           
           {'data': ['tg_id': '10011'}}

'''

f3()


# photo_path = f'{name_photo}'
# with open(photo_path, 'wb') as file:
#     file.write(img)











import io
from io import BytesIO
from pprint import pprint

import requests






# with open(filename, 'wb') as file:
#     file.write(response.content)