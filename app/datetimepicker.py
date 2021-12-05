from flask import Flask, render_template
from flask_wtf import Form
from wtforms.fields import DateField
from app import webapp


class MyForm(Form):
    date = DateField(id='datepick')


@webapp.route('/datepick')
def index():
    form = MyForm()
    return render_template('event/datetimepicker.html', form=form)