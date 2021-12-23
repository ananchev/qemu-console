from functools import wraps
from flask import Blueprint, render_template, Response, request
from flask.json import jsonify
from pygtail import Pygtail
import os, time, errno
from zipfile import ZipFile
from io import BytesIO

from libs.logger import logger, LOG_FILE
logger = logger.getChild('webapp')

import libs.management
mgmt_console = libs.management.QEMUManagement()

import libs.backup
bckp_console = libs.backup.QEMUBackup()

main = Blueprint('main', __name__)


# apply to disallow disruptive operations like shut down and power off while backups are running
def check_if_backup_is_ongoing(func):
    @wraps(func)
    def decorated_function(*args, **kws):
        if bckp_console.backup_is_ongoing:
            return ('', 204)
        return func(*args, **kws)
    return decorated_function


@main.route('/')
def index():
    #togeher with read_from_end parameter for Pygtail, below ensures Pygtail does not load logfile history when loading web console
    remove_pygtail_offset() 
    #time.sleep(0.5)
    #logger.info("Application console open")
    return render_template('index.html')


@main.route('/log')
def progress_log():
    def generate():
        for line in Pygtail(LOG_FILE, every_n=1, read_from_end=True):
            yield "data:" + str(line) + "\n\n"
            time.sleep(0.2)
    return Response(generate(), mimetype= 'text/event-stream')


@main.route('/start_vm')
def run_start_vm():
    vm_name = request.args.get('vm')
    retval = mgmt_console.start_vm(vm_name)
    return jsonify(retval)


@main.route('/shutdown_vm')
@check_if_backup_is_ongoing
def run_shutdown_vm():
    vm_name = request.args.get('vm')
    retval = mgmt_console.shutdown_vm(vm_name)
    return jsonify(retval)


@main.route('/poweroff_vm')
@check_if_backup_is_ongoing
def run_poweroff_vm():
    vm_name = request.args.get('vm')
    retval = mgmt_console.poweroff_vm(vm_name)
    return jsonify(retval)


@main.route('/reset_vm')
@check_if_backup_is_ongoing
def run_reset_vm():
    vm_name = request.args.get('vm')
    retval = mgmt_console.reset_vm(vm_name)
    return jsonify(retval)


@main.route('/backup_vm')
@check_if_backup_is_ongoing
def run_backup_vm():
    vm_name = request.args.get('vm')
    backup_target = request.args.get('target')
    retval = bckp_console.backup_vm(vm_name, backup_target)
    return jsonify(retval) 


@main.route('/vm_status')
def run_vm_status():
    retval = mgmt_console.fetch_running_vms()
    return jsonify(retval)


@main.route('/host_shutdown')
def shutdown_vms_at_host_reboot():
    mgmt_console.shutdown_vms_at_host_restart()
    return ('', 204)


@main.route('/host_startup')
def start_vms_at_host_startup():
    mgmt_console.start_vms_at_host_startup()
    return ('', 204)


@main.route('/get_logs')
def download_logs():
    memory_file = BytesIO()
    with ZipFile(memory_file, 'w') as zip_obj:
        # Iterate over all the files in directory
        for dirpath, dirnames, filenames in os.walk('logs'):
            for filename in filenames:
                zip_obj.write(os.path.join(dirpath, filename), 
                              os.path.relpath(os.path.join(dirpath, filename), os.path.join(dirpath, '..')))
    memory_file.seek(0)
    return Response(
        memory_file,
        mimetype="application/zip",
        headers={"Content-disposition":
                 "attachment; filename=logs.zip"})


def remove_pygtail_offset():
    try:
        os.remove(LOG_FILE+".offset")
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise