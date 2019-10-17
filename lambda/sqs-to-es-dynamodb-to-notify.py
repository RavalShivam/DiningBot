import json
import boto3
from botocore.vendored import requests
import logging
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    sqsClient = boto3.resource('sqs')
    smsClient = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelpRestaurants')    
    queue = sqsClient.get_queue_by_name(QueueName = "dinigbot")
    url = "https://search-restaurant-r4ctgoawcdpbntdr2oeyqhxsqi.us-east-1.es.amazonaws.com/"
    index = "restaurant/"
    search = "_search"
    esURL = url + index + search
    for message in queue.receive_messages():
        print("Message: ", message.body)
        data = json.loads(message.body)
        print('Data from Queue', data)
        cuisine = data['cuisine']
        time = data['time']
        people = data['people']
        location = data['location']
        date=data['date']
        phone_number = data['phone_number']
        json_data = {
          	"size": 3,
          	"query": {
          	"match": {
                "cuisine":cuisine
              }
          	},
          	"highlight": {
          	  "fields": {
          	  "id": {}
          	}
          	}
          }
        headers = { "Content-Type" : "application/json" }
        response = requests.post(esURL, data = json.dumps(json_data) , headers=headers)
        dict = response.json()
        sizeOfDict = len(dict["hits"]["hits"])
        rests = []
        for i in range(min(3,sizeOfDict)):
            rests.append(dict["hits"]["hits"][i]["_source"]["id"])
        print('Rests: ',rests)            
        res_dets=[]
        pe = "#nm, address"
        for r in rests:
            resp = table.scan(
                FilterExpression=Key('id').eq(r),
                ProjectionExpression=pe,
                ExpressionAttributeNames={ "#nm": "name" }   
            )
            print("DAta raw: ", resp['Items'])
            rest_js = json.loads(json.dumps(resp['Items']))
            print('From DB: ',rest_js)
            t = {}
            t['name'] = rest_js[0]['name']
            t["address"] = rest_js[0]['address'].replace("'","")
            res_dets.append(t)
        sms = "Hello. Here are my {} restaurant suggestions for {} people , for {} at {}".format(cuisine,people,date,time) + "\n"
        i=1
        for entries in res_dets:
            sms+=str(i)+". "
            
            sms+= entries["name"]+", located at "
            sms+=entries["address"]
            sms+="\n"
            i+=1    
        ph= phone_number if '+1' in phone_number else "+1"+ phone_number
        smsClient.publish(
        PhoneNumber=ph,
        Message=sms
            )
        print("Phone Number: ",ph)
        message.delete()