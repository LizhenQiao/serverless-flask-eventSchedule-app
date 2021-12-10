"""
Please note that this is a function for AWS lambda.
"""
import json
import urllib.parse
import boto3

KEY = 'AKIAU7TOV7Y25ESZI7RS'
SECRET = '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'
S3_BUCKET = 'a3avatars'

print('Loading function')

s3 = boto3.client('s3')

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        
        avatarsList = ['default.jpg']
        dynamoTable = dynamodb.Table('users')
        res = dynamoTable.scan()
        data = res["Items"]
        for item in data:
            if 'avatar' in item and item['avatar']:
                avatarsList.append(item['avatar'].split('/')[-1])
        res = s3.list_objects(Bucket=S3_BUCKET)
        if not 'Contents' in res:
            return None
        data = res['Contents']
        for content in data:
            file_name = content['Key']
            if file_name not in avatarsList:
                s3.delete_object(Bucket=S3_BUCKET, Key=file_name)
        return None
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
