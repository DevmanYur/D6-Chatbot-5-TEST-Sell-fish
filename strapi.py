import os
from pprint import pprint
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
load_dotenv()

strapi_tokenq = os.getenv("STRAPI_TOKEN")
headersq = {'Authorization': f'Bearer {strapi_tokenq}'}
response0 = requests.get(f'http://localhost:1337/api/products/vf9v1zcox2ugiha5zkaqgnm7?populate=picture',headers=headersq)
productq = response0.json()

url_picq = productq['data']['picture']['formats']['thumbnail']['url']

name_photo = productq['data']['picture']['formats']['thumbnail']['name']
# name_photo = 'ddqq'
response22 = requests.get(f'http://localhost:1337{url_picq}')
response22.raise_for_status()

image_data22 = BytesIO(response22.content)
img = Image.open(image_data22)
img.save('img1.png')



# photo_path = f'{name_photo}'
# with open(photo_path, 'wb') as file:
#     file.write(img)











import io
from io import BytesIO
from pprint import pprint

import requests






# with open(filename, 'wb') as file:
#     file.write(response.content)