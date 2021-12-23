import time, os.path
from datetime import datetime
from timeit import default_timer as timer

from libs.console import QEMUConsole

# Establish logging
from libs.logger import logger
logger = logger.getChild('backup')



class QEMUBackup(QEMUConsole):

    # when backup is ongoing, stores the resp. VM name
    backup_ongoing_for = None 

    def __init__(self) -> None:
        super().__init__()


    # below is used to implement logic to block other operations whilst backups are ongoing
    @property
    def backup_is_ongoing(self):
        if self.backup_ongoing_for is not None:
            logger.info(f"Backup is ongoing for '{self.backup_ongoing_for}'. No other commands can be executed before its completion.")
            return True
        return False


    def backup_vm(self,vm_name, backup_target=None):
        if not self._vm_running(vm_name):
            return {vm_name:"process not running"}

        if backup_target is None:
            backup_target = f"{self.conf['Locations']['backups']}/{vm_name}_{self._current_date_time()}.qcow2"

        command = "drive-mirror"
        arguments = {
                        "device": self.conf['Identifiers']['os_disk_id'],
                        "job-id": f"job-bckp-{vm_name}",
                        "target": f"{backup_target}",
                        "sync": "full"
                    }
        
        backup_start = timer()
        self.execute_QMP_command(vm_name,command,arguments)
        self.backup_ongoing_for = vm_name

        backup_completed = False
        while not backup_completed:
            backup_completed = self._backup_job_competed()
            time.sleep(5)
            logger.info(f"Backup is ongoing for '{self.backup_ongoing_for}', please wait...")
        
        command = "block-job-cancel"
        arguments = {
                        "device": f"job-bckp-{vm_name}"
                    }
        self.execute_QMP_command(vm_name,command,arguments)

        backup_end = timer()
        backup_size_GB = round(os.path.getsize(f"{backup_target}")/(1024*1024*1024),2)
        backup_filename =  os.path.basename(backup_target)
        logger.info(f"Backup '{backup_filename}' completed in '{round(backup_end-backup_start)}s', file size '{backup_size_GB}' GB")
        self.backup_ongoing_for = None
        return {vm_name: backup_filename}


    def _vm_running(self, vm_name):
        super().fetch_running_vms()
        if not self.vms.get(vm_name):
            logger.info(f"Virtual machine '{vm_name}' does not exist.")
            return False
        if self.vms[vm_name]["process"] in "not running":
            logger.info(f"Virtual machine '{vm_name}' is not running. Backup operation not possible")
            return False
        return True


    def _backup_job_competed(self):
        command = "query-block-jobs"

        retval = self.execute_QMP_command(self.backup_ongoing_for, command)

        ## running
        ## {'return': [{'auto-finalize': True, 'io-status': 'ok', 'device': 'job-bckp-manjaro', 'auto-dismiss': True, 'busy': True, 'len': 9137881088, 'offset': 2574450688, 'status': 'running', 'paused': False, 'speed': 0, 'ready': False, 'type': 'mirror'}]}
        
        ## ready
        ## {'return': [{'auto-finalize': True, 'io-status': 'ok', 'device': 'job-bckp-manjaro', 'auto-dismiss': True, 'busy': False, 'len': 9142599680, 'offset': 9142599680, 'status': 'ready', 'paused': False, 'speed': 0, 'ready': True, 'type': 'mirror'}]}
        return retval['return'][0]['ready']


    def _current_date_time(self):
        now = datetime.now()
        retval = now.strftime("%Y%m%d%H%M%S")
        return retval