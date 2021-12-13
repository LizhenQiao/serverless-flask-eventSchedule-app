<h1 align="center">Documentation of ece1779-A3</h1>

---

Entrance of App: https://2a9x6m52u3.execute-api.us-east-1.amazonaws.com/dev

- [Anouncement](#anouncement)
- [Introduction - how to use the web application](#introduction)
- [Details](#details)
- [Cost Model](#cost-model)

<br />

# Anouncement

In this document, we will explain the important parts of our application and introduce how to use it. If there is still anything unclear, please contact us at [lizhenqiao@mail.utoronto.ca](mailto:lizhenqiao@mail.utoronto.ca). We will also make an appointment to demonstrate our application as well.

<!-- <br />
<br /> -->

# Introduction

<h4>A serverless event schedule list application which have Remind, Friends and Appointments functions,  aims to improve the efficiency of work.</h4>

**Functions**
The details will be shown in the _Detail_ part.

---

**Client Side:**
IndexPage:

- Login
- Register
- Password Recovery

EventScheduleList:

- Add Event
- Remove Event
- Edit Event
- Search Event

FriendsSystem:

- Friends List
- See Friends Timetable
- Make Appointment

MessageBox:

- See Appointment Request from Friends

Others:

- Change Password
- Set Avatar
- Logout

---

**Server Side:**

- Main Application (API gateway + lambda implemented by Zappa)
- EventReminder (Amazon's SES Service + Lambda + API gateway)
- Garbage Collecting and Clearing (Lambda)
- S3, Dynamodb, etc

<!-- <br /> -->

---

## Architecture

**HighLevel Architecture**

<div style="display: flex; justify-content: flex-start">
  <div>
    <img src="./static/architecture.png"></img>
  </div>
</div>
<br />
<br />

**Code Architecture**

<div style="display: flex; justify-content: flex-start">
  <div>
    <img src="./static/code_architecture.png" style="width: 200px"></img>
  </div>
</div>
<br />
<br />

**Database Architecture**

Our database is based on Dynamodb. Actually NoSQL like Dynamodb have no certain architecture, but we think it is still worthwhile to represent our data structure in the database.

- **Users Table**(each item):

  - _user_name_: string
  - _avatar_: string
  - _event_: list
    - _event_name_: string
    - _event_desc_: string
    - _start_time_: string
    - _end_time_: string
  - _password_: string
  - _email_: string

- **Appointment Table**(each item):
  - _host_username_: string
  - _request_username_: string
  - _event_: list
    - _eventname_: string
    - _eventdesc_: string
    - _starttime_: string
    - _endtime_: string
    - _contact_: string
  - _read_: boolean

# Details

---

### IndexPage

**Index Page** is the first page you will see. It is basically the entrance of the app.
<img src="./static/indexpage.png"></img>

- **register**
  <img src="./static/register.png"></img>
- **password recovery**
  <img src="./static/password_recovery.png"></img>

---

### MainPage

**Main Page** is the home user page of the app. You could find all the functions in the navbar at the top area.
<img src="./static/main_page.png"></img>

---

### EventList

<img src="./static/eventlist_page.png"></img>

---

### FriendsList

<img src="./static/friends_list.png"></img>

- **friends timetable**, whiere you can make appointment with your friend. Your friends will get the message from **Message Box**.
  <img src="./static/friends_timetable.png"></img>

---

### Message Box

You could find the appointments requests from your friends in the **Message Box**.
<img src="./static/messagebox.png"></img>

---

### Set Avatar

You could set or change your avatar here, the used avatar will be deleted from s3 by our **garbage clearing** function in the background.
<img src="./static/set_avatar.png"></img>

---

### Garbage collection and clearing

We have a AWS lambda function used to auto-collect and clear the garbage files in our s3 bucket. It will be triggered when anything changed in the S3 bucket.

```
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

```

### Event reminder implemented by using AWS SES service.

```
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

```

# Cost Model

We use **AWS Pricing Calculator** to calclate our cost when we have 10, 1000, 1000,000 users. You could find details in _./cost_model.csv_

---

**Assumptions**:

- 50% of the users are _active_ users. For example: when we have 1000,000 users in total, 500,000 of them are active in average.
- Each user will make over 100 requests every month considering that our application is http-rich. (Acctually it is normal for a user to make thousands of requests per month. We made this over 200 assumption in case that in reality most of the user will not last.)

---

**Cost Model**
According to our Cost Model, we have the cost table of six months shown as below:

- 10 users: $33.9 per 6 months
- 1000 users: $527.82 per 6 months
- 1000,000 users: $38698.2 per 6 months
  <img src="./static/cost1.png"></img>

**Details of cost**

- **10 users**:
  <img src="./static/costdetail1.png"></img>
  <br />
  <br />
- 1000 users:
  <img src="./static/costdetail2.png"></img>
  <br />
  <br />
- 1000,000 users:
  <img src="./static/costdetail3.png"></img>
