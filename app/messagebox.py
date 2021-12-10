import boto3
from boto3.resources.model import Request
from app.config import KEY, SECRET
from .utils import login_required
from flask import render_template, session, flash, request
from app import webapp
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')


@webapp.route('/<string:user_name>/appointments', methods=['GET', 'POST'])
@login_required
def message_box(user_name):
	dynamoTable = dynamodb.Table('appointments')
	response = dynamoTable.query(
			KeyConditionExpression=Key('host_username').eq(user_name)
		)
	appointmentInfo = {}
	if response and 'Items' in response and response['Items']:
		appointmentInfo = response['Items'][0]
	return render_template('messagebox/messagebox.html', appointmentInfo=appointmentInfo)

	
