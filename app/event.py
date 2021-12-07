import boto3
from flask import Flask, redirect, url_for, request, render_template, session, flash
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired
from wtforms import validators, StringField, SubmitField
from datetime import datetime, timedelta
from .utils import login_required
from app.config import KEY, SECRET
from boto3.dynamodb.conditions import Key
from app import webapp

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')


class EventForm(FlaskForm):
    eventname = StringField('Event Name', validators=(validators.DataRequired(),))
    eventdesc = StringField('Event Description')
    starttime = DateTimeField('Start Time', default=datetime.now(), format='%Y/%m/%d %H:%M',
                              validators=(validators.DataRequired(),), id='startdatetimepicker')
    endtime = DateTimeField('End Time', default=datetime.now()+timedelta(minutes=30), format='%Y/%m/%d %H:%M',
                            validators=(validators.DataRequired(),), id='enddatetimepicker')
    submit = SubmitField('Submit')


# list all events
@webapp.route('/<string:user_name>/list_event', methods=['GET', 'POST'])
@login_required
def list_event(user_name):
    if request.method == 'GET':
        count = 0
        dynamoTable = dynamodb.Table('users')
        name_list = []
        desc_list = []
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
            name_list.append(event['name'])
            desc_list.append(event['desc'])
            starttime_list.append(event['start_time'])
            endtime_list.append(event['end_time'])
            count = count + 1
        return render_template('event/list_event.html', name_list=name_list, desc_list=desc_list,
                               starttime_list=starttime_list, endtime_list=endtime_list, count=count)
    elif request.method == 'POST':
        keyword = request.form['keyword']
        count = 0
        dynamoTable = dynamodb.Table('users')
        name_list = []
        desc_list = []
        starttime_list = []
        endtime_list = []
        response = dynamoTable.query(
            KeyConditionExpression=Key('user_name').eq(user_name)
        )
        items = response['Items']
        event_list = items[0]['event']
        for event in event_list:
            if keyword in event['name']:
                name_list.append(event['name'])
                desc_list.append(event['desc'])
                starttime_list.append(event['start_time'])
                endtime_list.append(event['end_time'])
                count = count + 1
        return render_template('event/list_event.html', name_list=name_list, desc_list=desc_list,
                               starttime_list=starttime_list, endtime_list=endtime_list, count=count)


# Add an event
@webapp.route('/<string:user_name>/add_event', methods=['GET', 'POST'])
@login_required
def add_event(user_name):
    eventform = EventForm()
    if eventform.validate_on_submit():
        if eventform.starttime.data <= eventform.endtime.data:
            eventname = eventform.eventname.data
            eventdesc = eventform.eventdesc.data
            starttime = eventform.starttime.data.strftime('%Y/%m/%d %H:%M')
            endtime = eventform.endtime.data.strftime('%Y/%m/%d %H:%M')
            dynamoTable = dynamodb.Table('users')
            dynamoTable.update_item(
                Key={
                    'user_name': user_name,
                },
                UpdateExpression='SET event = list_append(event, :vals)',
                ExpressionAttributeValues={
                    ':vals': [{'name': eventname,
                               'desc': eventdesc,
                               'start_time': starttime,
                               'end_time': endtime}]
                }
            )
            return redirect(url_for('list_event', user_name=user_name))
        else:
            flash("The end time of the event can't be earlier than the start time", category='error')
            return render_template('event/add_event.html', form=eventform)
    return render_template('event/add_event.html', form=eventform)


# Edit an event
@webapp.route('/<string:user_name>/edit_event/<string:event_name>', methods=['GET', 'POST'])
@login_required
def edit_event(user_name, event_name):
    eventform = EventForm()
    dynamoTable = dynamodb.Table('users')
    response = dynamoTable.query(
        KeyConditionExpression=Key('user_name').eq(user_name)
    )
    items = response['Items']
    event_list = items[0]['event']
    for event in event_list:
        if event['name'] == event_name:
            event_idx = event_list.index(event)
            # pre-fill data into the form for editing
            if request.method == 'GET':
                eventform.eventname.data = event['name']
                eventform.eventdesc.data = event['desc']
                eventform.starttime.data = datetime.strptime(event['start_time'], '%Y/%m/%d %H:%M')
                eventform.endtime.data = datetime.strptime(event['end_time'], '%Y/%m/%d %H:%M')
    if eventform.validate_on_submit():
        if eventform.starttime.data <= eventform.endtime.data:
            eventname = eventform.eventname.data
            eventdesc = eventform.eventdesc.data
            starttime = eventform.starttime.data.strftime('%Y/%m/%d %H:%M')
            endtime = eventform.endtime.data.strftime('%Y/%m/%d %H:%M')
            query = 'SET event[%d] = :vals' % (event_idx)
            dynamoTable.update_item(
                Key={
                    'user_name': user_name,
                },
                UpdateExpression=query,
                ExpressionAttributeValues={
                    ':vals': {'name': eventname,
                              'desc': eventdesc,
                              'start_time': starttime,
                              'end_time': endtime}
                }
            )
            return redirect(url_for('list_event', user_name=user_name))
    return render_template('event/edit_event.html', form=eventform)


# Remove an event
@webapp.route('/<string:user_name>/remove_event/<string:event_name>', methods=['POST'])
@login_required
def remove_event(user_name, event_name):
    if request.method == 'POST':
        dynamoTable = dynamodb.Table('users')
        # remove event in list
        response = dynamoTable.query(
            KeyConditionExpression=Key('user_name').eq(user_name)
        )
        items = response['Items']
        event_list = items[0]['event']
        for event in event_list:
            if event['name'] == event_name:
                event_idx = event_list.index(event)

        query = 'REMOVE event[%d]' % (event_idx)
        dynamoTable.update_item(
            Key={
                'user_name': user_name,
            },
            UpdateExpression=query
        )
        return redirect(url_for('list_event', user_name=user_name))
