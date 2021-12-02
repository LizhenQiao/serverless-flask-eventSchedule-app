from flask import Flask
webapp = Flask(__name__)
webapp.secret_key = "you-will-never-know-lol"
webapp.jinja_env.auto_reload = True
webapp.config['TEMPLATES_AUTO_RELOAD'] = True
webapp.config['SESSION_TYPE'] = 'filesystem'
from app import user
from app import main
# Background Thread for garbage collection 
from app import config
import time
import threading
import boto3
from app.config import KEY, SECRET, S3_BUCKET, S3_LOCATION



s3 = boto3.client(
    "s3",
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET
)

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')

# collect garbage and clear it.
def garbageHandler():
	while True:
		avatarsList = ['default.jpg']
		dynamoTable = dynamodb.Table('users')
		res = dynamoTable.scan()
		data = res["Items"]
		for item in data:
			if 'avatar' in item and item['avatar']:
				avatarsList.append(item['avatar'].split('/')[-1])
		res = s3.list_objects(Bucket=S3_BUCKET)
		if not 'Contents' in res:
			time.sleep(60)
			continue
		data = res['Contents']
		for content in data:
			file_name = content['Key']
			if file_name not in avatarsList:
				s3.delete_object(Bucket=S3_BUCKET, Key=file_name)
		time.sleep(60)

#  start the thread
global thread
thread = threading.Thread(target=garbageHandler)
thread.start()
