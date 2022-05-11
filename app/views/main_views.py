# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime

from flask import Blueprint, redirect, render_template
from flask import request, url_for, flash, session
from flask_user import current_user, login_required, roles_required
from flask_paginate import Pagination, get_page_parameter, get_page_args
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import InputRequired

from app import db, babel
from app.models.user_models import UserProfileForm, User
from app.models.report_models import Report

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'zh_CN')


# The Home page is accessible to anyone
@main_blueprint.route('/')
def home_page(limit=3):
    search = False
    q = request.args.get('q')
    if q:
        search = True

    page, per_page, offset = get_page_args()

    reports = Report.query.join(User).with_entities(Report.id, Report.title, Report.requested_at, User.first_name,
                                                    User.last_name, Report.sn).order_by(Report.id.desc())
    reports_for_render = reports.limit(per_page).offset(offset)

    pagination = Pagination(page=page, total=reports.count(), offset=offset, per_page=per_page, record_name='List',
                            search=search)

    return render_template('main/home_page.html', reports=reports_for_render, pagination=pagination)


class AddReport(FlaskForm):
    title = StringField(u'签报标题', validators=[InputRequired('Title is required')])
    drafted_by = SelectField(u'起草人', coerce=int, validators=[InputRequired('Drafter is required')])
    submit = SubmitField(u'登记签报')


# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/member', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def member_page():
    users = db.session.query(User).all()
    # Now forming the list of tuples for SelectField
    users_list = [(user.id, user.first_name + user.last_name) for user in users]
    form = AddReport(request.form, obj=current_user)
    # passing users_list to the form
    form.drafted_by.choices = users_list
    # set the default value
    form.drafted_by.data = current_user.id if current_user else 1

    if request.method == 'POST' and form.validate():
        report = Report(title=form.title.data,
                        requested_at=datetime.datetime.utcnow(),
                        drafted_by=form.drafted_by.data)
        db.session.add(report)
        db.session.flush()
        report.sn = Report.gen_sn(report.id)
        db.session.commit()
        flash(report.sn)

    return render_template('main/user_page.html', form=form)


# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')


@main_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.home_page'))

    # Process GET or invalid POST
    return render_template('main/user_profile_page.html',
                           form=form)
