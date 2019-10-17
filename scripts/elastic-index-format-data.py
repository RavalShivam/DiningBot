from __future__ import print_function
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://dynamodb.us-east-1.amazonaws.com")

table = dynamodb.Table('yelpRestaurants')
pe = "id, cuisine"
# Expression Attribute Names for Projection Expression only.
ean = { "#id": "id" }
esk = None

response = table.scan(ProjectionExpression=pe)
elr=[]
x=1
for i in response['Items']:
    el=json.dumps(i, cls=DecimalEncoder)
    elr.append("{ \"create\" : { \"_index\" : \"restaurant\", \"_type\" : \"_doc\", \"_id\" : \""+str(x)+"\" } }")
    x=x+1
    elr.append(el)
    print(el)


while 'LastEvaluatedKey' in response:
    response = table.scan(
        ProjectionExpression=pe,
        ExclusiveStartKey=response['LastEvaluatedKey']
        )
    for i in response['Items']:
        el=json.dumps(i, cls=DecimalEncoder)
        elr.append("{ \"create\" : { \"_index\" : \"restaurant\", \"_type\" : \"_doc\", \"_id\" : \""+str(x)+"\" } }")
        x=x+1
        elr.append(el)
        print(el)
print(len(elr))
with open('elsR.json', 'w') as outfile:
  json.dump(elr, outfile)
