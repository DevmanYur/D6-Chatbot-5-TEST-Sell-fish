import os
from pprint import pprint
import requests
from dotenv import load_dotenv

load_dotenv()

strapi_token = os.getenv("STRAPI_TOKEN")

headers = {'Authorization': f'Bearer {strapi_token}'}


response = requests.get(f'http://localhost:1337/api/products',
                        headers=headers)


products = response.json()


for product in products['data']:
    pprint(product)
