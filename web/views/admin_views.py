__author__ = 'Alimohammad'
from flask import request, render_template, abort, url_for, redirect
from flask_login import login_required, current_user
from data_model import Device
from functools import wraps
from flask import Blueprint

import datetime

admin_views = Blueprint('admin_views', __name__, template_folder='templates')


def admin_required(main_function):
    @wraps(main_function)
    def new_function(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        else:
            return main_function(*args, **kwargs)
    return new_function

@admin_views.route('/admin/')
@login_required
@admin_required
def index():
    return render_template("admin/admin_index.html")


@admin_views.route('/admin/devices/')
@login_required
@admin_required
def devices_view():
    devices = Device.find_all_devices()
    return render_template("admin/admin_devices.html", devices=devices)


@admin_views.route('/admin/device/<device_id>/')
@login_required
@admin_required
def device_view(device_id):
    device = current_user.get_device(device_id)
    if device is not None:
        pmv_ppv_list = device.get_pmv_ppv_list(datetime.datetime.utcnow() + datetime.timedelta(days=-1))
        occupancy_temperature_list = device.get_occupancy_temperature_list(datetime.datetime.utcnow() +
                                                                           datetime.timedelta(days=-1))
        owner = device.get_owner()
        return render_template("admin/admin_device.html", device=device, pmv_ppv_list=pmv_ppv_list,
                               occupancy_temperature_list=occupancy_temperature_list, device_owner=owner)
    else:
        abort(403)
