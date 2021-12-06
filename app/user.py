import boto3
import os
import urllib.request
from flask import render_template, request, redirect, url_for, session, flash
from app import webapp
from passlib.hash import sha256_crypt
from .utils import login_required
from werkzeug.utils import secure_filename
from app.config import KEY, SECRET, S3_BUCKET, S3_LOCATION
from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client(
    "s3",
    aws_access_key_id=KEY,
    aws_secret_access_key=SECRET
)
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET,
                          region_name='us-east-1')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@webapp.route('/<string:user_name>/change_pw', methods=['GET', 'POST'])
@login_required
def change_pw(user_name):
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
            return render_template('user/change_pw.html', user_name=session['username'])
    else:
        return render_template('user/change_pw.html')


# Upload avatar
@webapp.route('/<string:user_name>/upload', methods=['GET', 'POST'])
@login_required
def upload_avatar(user_name):
    if request.method == 'POST':
        if request.files['img']:
            f = request.files['img']
            # set the cursor to the file's position
            f.seek(0, 2)
            file_length = f.tell()
            if file_length > 1024 * 1024:
                flash('Error:Image size is too large', category='error')
                return render_template('image/image_upload.html')
            # set the cursor back to the original position
            f.seek(0)
            if f and allowed_file(f.filename):
                fname = secure_filename(f.filename)
                ftype = fname.rsplit('.', 1)[1].lower()
                url_o = S3_LOCATION + fname
                try:
                    s3.upload_fileobj(f, S3_BUCKET, fname, ExtraArgs={
                        'ACL': 'public-read', 'ContentType': ftype})
                except:
                    flash('Something wrong when uploading the image.',
                          category='error')
                finally:
                    dynamoTable = dynamodb.Table('users')
                    dynamoTable.update_item(
                        Key={
                            'user_name': session['username'],
                        },
                        UpdateExpression='SET avatar = :val1',
                        ExpressionAttributeValues={
                            ':val1': url_o
                        }
                    )

            else:
                flash('Error:Wrong image type', category='error')
                return render_template('image/image_upload.html')

            flash('Upload successfully', category='info')
            return render_template('image/image_upload.html')
    else:
        return render_template('image/image_upload.html')
