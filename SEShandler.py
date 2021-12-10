"""
Please note that this is a function for AWS lambda.
"""
import json
import boto3
import datetime

ses = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')
dynamoTable = dynamodb.Table('users')

def lambda_handler(event, context):
    response = dynamoTable.scan(
            ProjectionExpression='user_name, email, event'
        )
    items = response['Items']
    for item in items:
        username = item['user_name']
        email = item['email']
        event_list = item['event']
        print(event_list)
        for event in event_list:
            end_event = datetime.datetime.strptime(event['end_time'], '%Y/%m/%d %H:%M')
            now = datetime.datetime.now()
            time_now = datetime.datetime.strptime(now.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
            delta = end_event - time_now
            if delta.days <= 5:
                email_from = 'ece1779project@163.com'
                email_to = item['email']
                emaiL_subject = 'Event Reminder'
                email_body = "Hi, {} You have an event {} whose endtime is {}".format(username, event['name'], event['end_time'])
                response = ses.send_email(
                    Source = email_from,
                    Destination={
                        'ToAddresses': [
                            email_to,
                        ],
                    },
                    Message={
                        'Subject': {
                            'Data': emaiL_subject
                        },
                        'Body': {
                            'Text': {
                                'Data': email_body
                            }
                        }
                    }
                )
    return "Reminder has been sent."
    