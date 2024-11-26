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
    strapi_tokenq667 = os.getenv("STRAPI_TOKEN")
    headersq667 = {'Authorization': f'Bearer {strapi_tokenq667}'}

    tg_id = '710011'
    tg_id_for_strapi = f'tg_id_{tg_id}'
    print( tg_id_for_strapi)

    data = {'data': {'tg_id': tg_id_for_strapi}}

    response0667 = requests.post(f'http://localhost:1337/api/carts', headers=headersq667, json = data)
    productq667 = response0667.json()
    pprint(productq667)

'''
{'data': [{'createdAt': '2024-11-21T13:29:51.740Z',
           'documentId': 'yyl0wssrpdz3oku2xidfnof9',
           'id': 2,
           'publishedAt': '2024-11-21T13:29:52.839Z',
           'tg_id': '1001',
           'updatedAt': '2024-11-21T13:29:52.823Z'}}
           
           {'data': ['tg_id': '10011'}}

'''

def f4():
    'GET /api/users?filters[username][$eq]=John'
    strapi_tokenq66 = os.getenv("STRAPI_TOKEN")
    headersq66 = {'Authorization': f'Bearer {strapi_tokenq66}'}
    tg_id = '710011'
    tg_id_for_strapi = f'tg_id_{tg_id}'
    response066 = requests.get(f'http://localhost:1337/api/carts?filters[tg_id][$eq]={tg_id_for_strapi}', headers=headersq66)
    productq66 = response066.json()

    if productq66['data']:
        print("Блок А")
        print("здесь что то есть")
        print('documentId :', productq66['data'][0]['tg_id'])
        print('documentId :' , productq66['data'][0]['documentId'])
    else:
        print("Блок Б")
        print("здесь пусто")
        print("создаем новый ")

        strapi_tokenq667 = os.getenv("STRAPI_TOKEN")
        headersq667 = {'Authorization': f'Bearer {strapi_tokenq667}'}

        data = {'data': {'tg_id': tg_id_for_strapi}}

        response0667 = requests.post(f'http://localhost:1337/api/carts', headers=headersq667, json=data)
        productq667 = response0667.json()
        print("Теперь: ")
        pprint(productq667)




def  f5():
    strapi_tokenq66 = os.getenv("STRAPI_TOKEN")
    headersq66 = {'Authorization': f'Bearer {strapi_tokenq66}'}
    tg_id = '710011'
    tg_id_for_strapi = f'tg_id_{tg_id}'
    vremenno = '1001'
    response066 = requests.get(f'http://localhost:1337/api/carts?filters[tg_id][$eq]={vremenno}',
                               headers=headersq66)
    productq66 = response066.json()
    print("Блок А")
    print("здесь что то есть")
    print('tg_id :', productq66['data'][0]['tg_id'])
    print('documentId :', productq66['data'][0]['documentId'])

    print("===========")
    documentId_ = productq66['data'][0]['documentId']

    response = requests.get(f'http://localhost:1337/api/carts/{documentId_}?populate[cartitems][populate][0]=product',headers=headersq66)
    productq667 = response.json()
    pprint(productq667)
    '?populate=cartitems'

def f6():
    strapi_tokenq667 = os.getenv("STRAPI_TOKEN")
    headersq667 = {'Authorization': f'Bearer {strapi_tokenq667}'}

    data = {'data': {'quantity': 200,
                     'product': 'ylokeva71vdpe8xxs57nxdnv',
                     'cart': 'efsb9hcihq106x3jj5s9ut2r'


                     }}
    response0667 = requests.post(f'http://localhost:1337/api/cartitems', headers=headersq667, json=data)
    productq667 = response0667.json()
    pprint(productq667)

    gg = '''{
  data: {
    categories: {
      set: ['z0y2x4w6v8u1t3s5r7q9onm', 'j9k8l7m6n5o4p3q2r1s0tuv4'],
    }
  }
}

    '''
'''
/api/books
?
sort[0]=title:asc
&
filters[title][$eq]=hello
&
populate[author][fields][0]=firstName
&
populate[author][fields][1]=lastName
&
fields[0]=title
&
pagination[pageSize]=10
&
pagination[page]=1
&
status=published
&
locale=en

populate[0]=relation-name
&
populate[1]=another-relation-name
&
populate[2]=yet-another-relation-name

GET /api/articles?
populate[category][populate][0]=restaurants
'''



def f7():
    strapi_tokenq667 = os.getenv("STRAPI_TOKEN")
    headersq667 = {'Authorization': f'Bearer {strapi_tokenq667}'}
    response0667 = requests.get(f'http://localhost:1337/api/cartitems/ihudrhuxqbyo8z9rbeiw09ku?populate=product&populate=cart', headers=headersq667)
    productq667 = response0667.json()
    pprint(productq667)

'''
{'data': {'cart': {'createdAt': '2024-11-21T13:29:51.740Z',
                   'documentId': 'yyl0wssrpdz3oku2xidfnof9',
                   'id': 2,
                   'publishedAt': '2024-11-21T13:29:52.839Z',
                   'tg_id': '1001',
                   'updatedAt': '2024-11-21T13:29:52.823Z'},
          'createdAt': '2024-11-21T13:30:39.847Z',
          'documentId': 'ihudrhuxqbyo8z9rbeiw09ku',
          'id': 2,
          'product': {'createdAt': '2024-11-12T07:11:08.174Z',
                      'description': 'Вес: 80-110 гр/штука Кол-во: 9-11 штук в '
                                     '1 кг.',
                      'documentId': 'ylokeva71vdpe8xxs57nxdnv',
                      'id': 8,
                      'price': 3800,
                      'publishedAt': '2024-11-12T07:11:08.189Z',
                      'title': 'Живые раки (отборные)',
                      'updatedAt': '2024-11-12T07:11:08.174Z'},
          'publishedAt': '2024-11-21T13:30:40.987Z',
          'quantity': 1,
          'updatedAt': '2024-11-21T13:30:40.977Z'},
 'meta': {}}
'''


def post_cartitems(cart, product, quantity):
    strapi_tokenq667 = os.getenv("STRAPI_TOKEN")
    headersq667 = {'Authorization': f'Bearer {strapi_tokenq667}'}

    data = {'data': {'quantity': quantity,
                     'product': product,
                     'cart': cart
                     }}
    response0667 = requests.post(f'http://localhost:1337/api/cartitems', headers=headersq667, json=data)
    productq667 = response0667.json()

def f8():
    strapi_tokenq = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_tokenq}'}

    vremenno = '1001'
    carts_filters_response = requests.get(
        f'http://localhost:1337/api/carts?filters[tg_id][$eq]={vremenno}',
        headers=headers)
    carts_filters = carts_filters_response.json()
    posledniy_element = carts_filters['data'][-1]['documentId']
    print(posledniy_element)
    print()

    posledniy_element_response = requests.get(
        f'http://localhost:1337/api/carts/{posledniy_element}?populate[cartitems][populate][0]=product',
        headers=headers)

    podrobnee_o_obekte = posledniy_element_response.json()

    pprint(podrobnee_o_obekte)






    # tg_id = '710011'
    # tg_id_for_strapi = f'tg_id_{tg_id}'
    # vremenno = '1001'
    # response066 = requests.get(f'http://localhost:1337/api/carts?filters[tg_id][$eq]={vremenno}',
    #                            headers=headersq66)




f8()

import io
from io import BytesIO
from pprint import pprint

import requests






# with open(filename, 'wb') as file:
#     file.write(response.content)