from flask import render_template, request, redirect, url_for, session, flash
from app import webapp
import boto3
from passlib.hash import sha256_crypt
from .utils import login_required
from app.config import KEY, SECRET
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')


@webapp.route('/<string:username>/change_pw', methods=['GET', 'POST'])
@login_required
def change_pw(username):
    if request.method == 'POST':
        if request.form['new_password'] == '':
            flash("Error:Password can't be empty", category='error')
            return render_template('user/change_pw.html')
        else:
            new_password = request.form['new_password']
            hash_password = sha256_crypt.hash(new_password)
            dynamoTable = dynamodb.Table('users')
            dynamoTable.update_item(
                Key={
                    'user_name': session['username'],
                },
                UpdateExpression='SET password = :val1',
                ExpressionAttributeValues={
                    ':val1': hash_password
                }
            )
            flash('Password change Successfully', category='info')
            return render_template('user/change_pw.html', username=session['username'])
    else:
        return render_template('user/change_pw.html')