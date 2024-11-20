import os
from pprint import pprint
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
load_dotenv()



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





# photo_path = f'{name_photo}'
# with open(photo_path, 'wb') as file:
#     file.write(img)











import io
from io import BytesIO
from pprint import pprint

import requests






# with open(filename, 'wb') as file:
#     file.write(response.content)