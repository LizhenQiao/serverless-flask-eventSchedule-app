import boto3
from boto3.dynamodb.conditions import Key, Attr
from config import KEY, SECRET

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')
dynamoTable = dynamodb.Table('users')
eventname = 'ece1762'
starttime = '2021-12-04 18:00'
endtime = '2021-12-04 19:00'
# add new event to the end of the list
# dynamoTable.update_item(
#     Key={
#         'user_name': 'Jiahao',
#     },
#     UpdateExpression='SET event = list_append(event, :vals)',
#     ExpressionAttributeValues={
#         ':vals': [{'name': eventname,
#                    'start_time': starttime,
#                    'end_time': endtime}]
#     }
# )
# # remove event in list
# response = dynamoTable.query(
#     KeyConditionExpression=Key('user_name').eq('Jiahao')
# )
# items = response['Items']
# event_list = items[0]['event']
# for event in event_list:
#     if event['name'] == 'ece1762':
#         event_idx = event_list.index(event)
#
# query = 'REMOVE event[%d]" % (event_idx)'
# dynamoTable.update_item(
#     Key={
#         'user_name': 'Jiahao',
#     },
#     UpdateExpression=query
# )

# edit event in list
# response = dynamoTable.query(
#     KeyConditionExpression=Key('user_name').eq('Jiahao')
# )
# items = response['Items']
# event_list = items[0]['event']
# for event in event_list:
#     if event['name'] == 'aps1070':
#         event_idx = event_list.index(event)
#
# query = 'SET event[%d] = :vals' % (event_idx)
# dynamoTable.update_item(
#     Key={
#         'user_name': 'Jiahao',
#     },
#     UpdateExpression=query,
#     ExpressionAttributeValues={
#         ':vals': {'name': eventname,
#                    'start_time': starttime,
#                    'end_time': endtime}
#     }
# )

# search event in list
# response = dynamoTable.query(
#     KeyConditionExpression=Key('user_name').eq('Jiahao')
# )
# items = response['Items']
# event_list = items[0]['event']
# for event in event_list:
#     if event['name'] == 'ece1762':
#         event_idx = event_list.index(event)
# print(event_list[event_idx])