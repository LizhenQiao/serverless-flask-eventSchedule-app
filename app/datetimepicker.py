from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms.fields import DateField
from app import webapp


class MyForm(FlaskForm):
    date = DateField(id='datepick')


@webapp.route('/datepick')
def index():
    form = MyForm()
    return render_template('event/datetimepicker.html', form=form)
