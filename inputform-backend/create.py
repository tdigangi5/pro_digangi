import json
import os
import time
import uuid
import boto3
from boto3.dynamodb.conditions import Key, Attr
dynamodb = boto3.resource('dynamodb')

class Decoder(json.JSONDecoder):
    def decode(self, s):
        result = super(Decoder, self).decode(s)
        return self._decode(result)

    def _decode(self, o):
        if isinstance(o, str) or isinstance(o, unicode):
            try:
                return int(o)
            except ValueError:
                return o
        elif isinstance(o, dict):
            return {k: self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o

def confirm_number():
    """
    fetch highest confirmation number for the
    """
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    response = table.scan(
        Select='SPECIFIC_ATTRIBUTES',
        AttributesToGet=[
            'confirm_code',
        ]
    )
    arr = []
    for i in response['Items']:
        item = json.dumps(i)
        int_item = json.loads(item, cls=Decoder)
        current_item = int_item['confirm_code']
        arr.append(current_item)
    if not arr:
        return 100000
    else:
        sort_arr = sorted(arr)
        max_num = sort_arr[-1]
        return max_num

def create(event, context):
    data = json.loads(event['body'])
    current_number = confirm_number()
    timestamp = int(time.time() * 1000)

    # Creating a table inside DynamoDBs
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    next_code = str(confirm_number() + 1)
    print(next_code)

    # Items to populate the table
    item = {
        'id': str(uuid.uuid1()),
        'confirm_code': next_code,
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'email': data['email'],
        'comments': data['comments'],
        'createdAt': timestamp,
        'updatedAt': timestamp
    }

    # write the item to the database
    table.put_item(Item=item)

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(item),
        "headers": {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Credentials": "true"
        }
    }

    return response
