from __future__ import print_function
import boto3
import codecs
import json
import time
import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://dynamodb.us-east-1.amazonaws.com")

table = dynamodb.Table('yelpRestaurants')

with open("scottish.json", "r", encoding='utf-8') as json_file:
  data= json.load(json_file)
  lis= data['restaurants']
  listOfReqs=[]
  i=0
  for item in lis:
    #item=json.load(item)
    id = item['id']
    alias = item['alias']
    name = item['name']
    image_url = "N/A" if not item['image_url'] else item['image_url']
    is_closed = item['is_closed']
    url = item['url']
    review_count = item['review_count']
    rating=str(item['rating'])
    coordinates=json.dumps(item["coordinates"])
    transactions=json.dumps(item["transactions"])
    price=item["price"] if "price" in item.keys() else "N/A"
    add=item["location"]
    display_add=json.dumps(add["display_address"])
    address= display_add if not add["address1"] else add["address1"]
    phone="N/A" if not item["display_phone"] else item["display_phone"]
    distance="0.0" if not str(item["distance"]) else str(item["distance"])
    cuisine=item['cuisine']
    date=str(datetime.datetime.now())
    print("Writing: ", id, alias, distance)
    print("Val: ",item)
    i=i+1
    if i%5==0:
        time.sleep(1)
    table.put_item(
        Item={
            'id': id,
           'alias': alias,
    'name' :name,
    'image_url':image_url,
    'is_closed' :is_closed,
    'url':url,
    'review_count':review_count,
    'rating':rating,
    'coordinates':coordinates,
    'transactions':transactions,
    'price':price,
    'display_add':display_add,
    'address':address,
    'phone':phone,
    'distance':distance,
    'timestamp':date,
    'cuisine':cuisine
        }
    )

print("Finished!")
