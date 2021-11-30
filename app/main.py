from flask import render_template, request, flash, url_for, session
from app import webapp
from app.config import KEY, SECRET
import boto3
from boto3.dynamodb.conditions import Key, Attr
from passlib.hash import sha256_crypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.utils import redirect
from .utils import login_required

webapp.config['MAIL_SERVER'] = 'smtp.163.com'
webapp.config['MAIL_PORT'] = 465
webapp.config['MAIL_USE_SSL'] = True
webapp.config['MAIL_USERNAME'] = "ece1779project@163.com"
webapp.config['MAIL_PASSWORD'] = "ADHSDYQJGZCGHRWW"

# Initialize flask_mail.
mail = Mail(webapp)

# Initialize timed-url-serializer.
s = URLSafeTimedSerializer("whateversecretkey")

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')


@webapp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        dynamoTable = dynamodb.Table('users')
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if username == "" or password == "" or email == "":
            flash("Error: Username, Password or Email can't be empty!", category='error')
            return render_template('user/register.html')
        response = dynamoTable.query(
            KeyConditionExpression=Key('user_name').eq(username)
        )
        items = response['Items']
        if not items:
            hash_password = sha256_crypt.hash(password)
            dynamoTable.put_item(
                Item={
                    'user_name': username,
                    'password': hash_password,
                    'email': email
                }
            )
            flash('Register Successfully', category='info')
            return redirect(url_for('register'))
        else:
            flash('Username already exists, please try another one', category='error')
            return render_template('user/register.html')
    else:
        return render_template('user/register.html')


@webapp.route('/', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        session.pop('username', None)
        username = request.form['username']
        password = request.form['password']
        dynamoTable = dynamodb.Table('users')
        response = dynamoTable.query(
            KeyConditionExpression=Key('user_name').eq(username)
        )
        items = response['Items']
        if not items:
            flash('Error password or username, please try again', category='error')
            return render_template('main.html', title='Login')
        else:
            if not sha256_crypt.verify(password, items[0]['password']):
                flash('Error password or username, please try again', category='error')
                return render_template('main.html')
            else:
                session['username'] = items[0]['user_name']
                return redirect(url_for('user_page', username=session['username']))
    else:
        return render_template('main.html', title='Login')


@webapp.route('/<string:username>', methods=['GET', 'POST'])
@login_required
def user_page(username):
    if username == session['username']:
        return render_template('user/user_page.html', username=session['username'])
    else:
        flash('url not matched', category='error')
        return redirect(url_for('user_login'))


@webapp.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':
        username = request.form['username']
        dynamoTable = dynamodb.Table('users')
        response = dynamoTable.query(
            KeyConditionExpression=Key('user_name').eq(username)
        )
        items = response['Items']
        if not items:
            flash('Username dose not exist, please register', category='error')
            return render_template("public/password_recovery.html")
        else:
            user_email = items[0]['email']
            token = s.dumps(user_email)
            msg = Message('Reset password for your account.',
                          sender="ece1779project@163.com", recipients=[user_email])
            link = url_for('reset_password', token=token, _external=True)
            msg.body = "Your link for reset your password is {}".format(link)
            mail.send(msg)
            return redirect(url_for('email_sent'))
    else:
        return render_template("public/password_recovery.html")


@webapp.route('/email_sent', methods=['GET'])
def email_sent():
    return render_template("public/email_sent.html")


@webapp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    dynamoTable = dynamodb.Table('users')
    try:
        t = s.loads(token, max_age=600)
        if request.method == 'POST':
            username = request.form['username']
            new_password = request.form['new_password']
            hash_password = sha256_crypt.hash(new_password)
            dynamoTable.update_item(
                Key={
                    'user_name': username,
                },
                UpdateExpression='SET password = :val1',
                ExpressionAttributeValues={
                    ':val1': hash_password
                }
            )
            return render_template('main.html', title='Login')
        elif request.method == 'GET':
            return render_template('public/reset_password.html')
    except SignatureExpired:
        return "<h1>The token is expired</h1>"


@webapp.route('/logout', methods=['GET', 'POST'])
def user_logout():
    session.clear()
    return redirect(url_for('user_login'))

