import time, subprocess

from libs.console import QEMUConsole

# Establish logging
from libs.logger import logger
logger = logger.getChild('management')

class QEMUManagement(QEMUConsole):
    
    def __init__(self) -> None:
        super().__init__()



    def fetch_running_vms(self):
        retval = super().fetch_running_vms()
        self._log_vm_info()
        return retval



    def start_vm(self, vm_name):
        if super()._is_vm_process_running(vm_name):
            logger.info(f"QEMU process for '{vm_name}' is already running")
            return
        command = ["/bin/bash", f"{self.conf['Locations']['scripts']}/start-vm-{vm_name}"]
        p = subprocess.Popen(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"'{vm_name}' is starting up, please wait...")

        i = 0
        while i < 15:
            ret = p.poll()
            if ret is not None: # different than None means process has terminated
                out, err = p.communicate()
                logger.info(f"Error {p.returncode}: {err}")
                super().fetch_running_vms()
                self._log_vm_info()
                return
            time.sleep(1)
            i = i + 1 
        super().fetch_running_vms()
        self._log_vm_info()



    def shutdown_vm(self, vm_name):
        qmp_command="system_powerdown"
        retval = super()._execute_QMP_command(vm_name,qmp_command)
        if retval:
            logger.info(f"'{vm_name}' is shutting down, please wait...")
            time.sleep(10)
            super().fetch_running_vms()
            self._log_vm_info()
        else:
            logger.info(f"No action was executed")



    def poweroff_vm(self, vm_name):
        qmp_command="quit"
        retval = super()._execute_QMP_command(vm_name,qmp_command)
        if retval:
            logger.info(f"'{vm_name}' process was terminated")
            super().fetch_running_vms()
            self._log_vm_info()
        else:
            logger.info(f"No action was executed")



    def reset_vm(self, vm_name):
        qmp_command="system_reset"
        retval = super()._execute_QMP_command(vm_name,qmp_command)
        if retval:
            logger.info(f"reset was performed on '{vm_name}', please wait...")
            time.sleep(10)
            super().fetch_running_vms()
            self._log_vm_info()
        else:
            logger.info(f"No action was executed")




    def _log_vm_info(self):
        for vm, vm_info in self.vms.items():
            vm_state = vm_info.get('status', None)
            if vm_state is None:
                logger.info(f"'{vm}' process is '{vm_info['process']}'")
            else:
                logger.info(f"'{vm}' process is '{vm_info['process']}' and the VM is in status '{vm_state}'")