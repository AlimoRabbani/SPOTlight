__author__ = 'Alimohammad'
from flask import request, render_template, abort, url_for, redirect
from flask_login import login_required, current_user
import datetime
import json
from urlparse import urlparse, urljoin

from flask import Blueprint

user_views = Blueprint('user_views', __name__, template_folder='templates')


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@user_views.route('/devices/')
@login_required
def devices_view():
    devices = current_user.find_devices()
    return render_template("users/devices.html", devices=devices)


@user_views.route('/device/<device_id>/')
@login_required
def device_view(device_id):
    device = current_user.get_device(device_id)
    if device is not None:
        return render_template("users/device.html", device=device)
    else:
        abort(403)

@user_views.route('/device/<device_id>/get_pmv_ppv_list/')
@login_required
def device_get_pmv_ppv_list(device_id):
    device = current_user.get_device(device_id)
    pmv_ppv_list = None
    if device is not None:
        if request.args.get("time_interval") == "Month":
            pmv_ppv_list = device.get_pmv_ppv_list(datetime.datetime.utcnow() + datetime.timedelta(weeks=-4))
        elif request.args.get("time_interval") == "Week":
            pmv_ppv_list = device.get_pmv_ppv_list(datetime.datetime.utcnow() + datetime.timedelta(weeks=-1))
        elif request.args.get("time_interval") == "Day":
            pmv_ppv_list = device.get_pmv_ppv_list(datetime.datetime.utcnow() + datetime.timedelta(days=-1))
        elif request.args.get("time_interval") == "Hour":
            pmv_ppv_list = device.get_pmv_ppv_list(datetime.datetime.utcnow() + datetime.timedelta(hours=-1))
        elif request.args.get("time_interval") == "Now":
            pmv_ppv_list = device.get_pmv_ppv_list(datetime.datetime.utcnow() + datetime.timedelta(minutes=-15))
        elif request.args.get("time_interval") == "Last":
            pmv_ppv_list = device.get_last_pmv_ppv()
        return json.dumps(pmv_ppv_list)
    else:
        abort(403)

@user_views.route('/device/<device_id>/get_occupancy_temperature_list/')
@login_required
def device_get_occupancy_temperature_list(device_id):
    device = current_user.get_device(device_id)
    occupancy_temperature_list = None
    if device is not None:
        if request.args.get("time_interval") == "Month":
            occupancy_temperature_list = device.get_occupancy_temperature_list(datetime.datetime.utcnow() + datetime.timedelta(weeks=-4))
        elif request.args.get("time_interval") == "Week":
            occupancy_temperature_list = device.get_occupancy_temperature_list(datetime.datetime.utcnow() + datetime.timedelta(weeks=-1))
        elif request.args.get("time_interval") == "Day":
            occupancy_temperature_list = device.get_occupancy_temperature_list(datetime.datetime.utcnow() + datetime.timedelta(days=-1))
        elif request.args.get("time_interval") == "Hour":
            occupancy_temperature_list = device.get_occupancy_temperature_list(datetime.datetime.utcnow() + datetime.timedelta(hours=-1))
        elif request.args.get("time_interval") == "Now":
            occupancy_temperature_list = device.get_occupancy_temperature_list(datetime.datetime.utcnow() + datetime.timedelta(minutes=-15))
        elif request.args.get("time_interval") == "Last":
            occupancy_temperature_list = device.get_last_occupancy_temperature()
        return json.dumps(occupancy_temperature_list)
    else:
        abort(403)


@user_views.route('/device/<device_id>/start_training/')
@login_required
def start_training(device_id):
    device = current_user.get_device(device_id)
    if device is not None:
        device.start_training()
        if is_safe_url(request.referrer):
            return redirect(request.referrer)
        else:
            return redirect(url_for("user_views.device_view", device_id=device.device_id))
    abort(403)

@user_views.route('/device/<device_id>/submit_vote/')
@login_required
def submit_vote(device_id):
    device = current_user.get_device(device_id)
    if device is not None:
        if device.submit_vote(int(request.args.get("value"))):
            return "ok"
    abort(403)

@user_views.route('/device/<device_id>/end_training/')
@login_required
def end_training(device_id):
    device = current_user.get_device(device_id)
    if device is not None:
        device.end_training()
        if is_safe_url(request.referrer):
            return redirect(request.referrer)
        else:
            return redirect(url_for("user_views.device_view", device_id=device.device_id))
    abort(403)


@user_views.route('/device/<device_id>/submit_offset/')
@login_required
def submit_offset(device_id):
    device = current_user.get_device(device_id)
    if device is not None:
        if device.update_offset(float(request.args.get("value"))):
            return "ok"
    abort(403)
