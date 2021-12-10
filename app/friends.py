import boto3
from flask import render_template, request, redirect, url_for, session, flash
from app import webapp
from .utils import login_required
from app.config import KEY, SECRET, S3_BUCKET, S3_LOCATION
from boto3.dynamodb.conditions import Key
from wtforms import validators, StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateTimeField
from datetime import datetime, timedelta

s3 = boto3.client(
    "s3",
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET
)

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')


class EventForm(FlaskForm):
    eventname = StringField(
        'Event Name', validators=(validators.DataRequired(),))
    eventdesc = StringField('Event Description')
    starttime = DateTimeField('Start Time', default=datetime.now(), format='%Y/%m/%d %H:%M',
                              validators=(validators.DataRequired(),), id='startdatetimepicker')
    endtime = DateTimeField('End Time', default=datetime.now()+timedelta(minutes=30), format='%Y/%m/%d %H:%M',
                            validators=(validators.DataRequired(),), id='enddatetimepicker')
    submit = SubmitField('Submit')


# Show friends list
@webapp.route('/<string:user_name>/friends', methods=['GET', 'POST'])
@login_required
def friends_list(user_name):
    dynamoTable = dynamodb.Table('users')
    res = dynamoTable.scan()
    items = res["Items"]
    userinfoList = []
    for item in items:
        if item['user_name'] == session['username']:
            continue
        if 'avatar' in item and item['avatar']:
            userinfoList.append((item["user_name"], item['avatar']))
        else:
            userinfoList.append(
                (item["user_name"], 'https://a3avatars.s3.amazonaws.com/default.jpg'))
    return render_template('friends/list_friends.html', userinfoList=userinfoList)


# list time schedule of a certain friend
@webapp.route('/<string:user_name>/timetable', methods=['GET', 'POST'])
@login_required
def show_timetable(user_name):
    count = 0
    dynamoTable = dynamodb.Table('users')
    starttime_list = []
    endtime_list = []
    response = dynamoTable.query(
        KeyConditionExpression=Key('user_name').eq(user_name)
    )
    items = response['Items']
    if items and 'event' in items[0] and items[0]['event']:
        event_list = items[0]['event']
    else:
        event_list = []
    for event in event_list:
        starttime_list.append(event['start_time'])
        endtime_list.append(event['end_time'])
        count = count + 1
    return render_template('friends/timetable.html', host_username=user_name,
                           starttime_list=starttime_list, endtime_list=endtime_list, count=count)


# make appointment with friends.
@webapp.route('/<string:request_username>/appointment/<string:host_username>', methods=['GET', 'POST'])
@login_required
def make_appointment(request_username, host_username):
    eventform = EventForm()
    userTable = dynamodb.Table('users')
    appointmentsTable = dynamodb.Table('appointments')
    response = userTable.query(
				KeyConditionExpression=Key('user_name').eq(request_username)
		)
    requestuser_contact = response['Items'][0]['email']
    host_occupiedTime = set()
    response = userTable.query(
				KeyConditionExpression=Key('user_name').eq(host_username)
		)
    items = response['Items']
    event_list = items[0]['event']
    for event in event_list:
        host_occupiedTime.add((datetime.strptime(
						event['start_time'], '%Y/%m/%d %H:%M'), datetime.strptime(event['end_time'], '%Y/%m/%d %H:%M')))
    if eventform.validate_on_submit():
        for starttime, endtime in host_occupiedTime:
            if starttime < eventform.starttime.data < endtime or starttime < eventform.endtime.data < endtime or (eventform.starttime.data < starttime and eventform.endtime.data > endtime):
                flash('Unavailable time period', category='error')
                return render_template('event/edit_event.html', form=eventform)
        if eventform.starttime.data <= eventform.endtime.data:
            eventname = eventform.eventname.data
            eventdesc = eventform.eventdesc.data
            starttime = eventform.starttime.data.strftime('%Y/%m/%d %H:%M')
            endtime = eventform.endtime.data.strftime('%Y/%m/%d %H:%M')
            appointmentsTable.put_item(
								Item={
										'host_username': host_username,
										'request_username': request_username,
										'event': {
												'eventname': eventname,
												'eventdesc': eventdesc,
												'contact': requestuser_contact,
												'starttime': starttime,
												'endtime': endtime
										},
										'read': False
								}
						)
            flash('Appointment has been sent.', category='info')		
    return render_template('friends/make_appointment.html', form=eventform, host_username=host_username)
