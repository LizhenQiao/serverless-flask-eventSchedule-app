import boto3
from boto3.dynamodb.conditions import Key, Attr
from config import KEY, SECRET
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')
dynamoTable = dynamodb.Table('users')
dynamoTable = dynamodb.Table('users')
response = dynamoTable.query(
    KeyConditionExpression=Key('user_name').eq('abc')
)
items = response['Items']
print(items[0])