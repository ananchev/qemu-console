import time, subprocess, pickle

from libs.console import QEMUConsole

# Establish logging
from libs.logger import logger
logger = logger.getChild('management')

class QEMUManagement(QEMUConsole):
    
    def __init__(self) -> None:
        super().__init__()



    def fetch_running_vms(self):
        super().fetch_running_vms()
        self._log_vm_info()
        return self.vms



    def start_vm(self, vm_name):
        if super().is_vm_process_running(vm_name):
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
                self.fetch_running_vms()
                return
            time.sleep(1)
            i = i + 1 
        self.fetch_running_vms()
        return self.vms


    def shutdown_vm(self, vm_name):
        qmp_command="system_powerdown"
        retval = self.execute_QMP_command(vm_name,qmp_command)
        if retval is not None:
            logger.info(f"'{vm_name}' is shutting down, please wait...")
            time.sleep(10)
            self.fetch_running_vms()
        else:
            logger.info(f"No action was executed")
        return self.vms


    def poweroff_vm(self, vm_name):
        qmp_command="quit"
        retval = self.execute_QMP_command(vm_name,qmp_command)
        if retval:
            logger.info(f"'{vm_name}' process was terminated")
            self.fetch_running_vms()
        else:
            logger.info(f"No action was executed")
        return self.vms


    def reset_vm(self, vm_name):
        qmp_command="system_reset"
        retval = self.execute_QMP_command(vm_name,qmp_command)
        if retval:
            logger.info(f"reset was performed on '{vm_name}', please wait...")
            time.sleep(10)
            self.fetch_running_vms()
        else:
            logger.info(f"No action was executed")
        return self.vms



    def _log_vm_info(self):
        for vm, vm_info in self.vms.items():
            vm_state = vm_info.get('status', None)
            if vm_state is None:
                logger.info(f"'{vm}' process is '{vm_info['process']}'")
            else:
                logger.info(f"'{vm}' process is '{vm_info['process']}' and the VM is in status '{vm_state}'")

   
    def shutdown_vms_at_host_restart(self):
        logger.info(f"Host shutdown command received, capturing running VMs...")
        super().fetch_running_vms()
        running_vms = []
        for vm, vm_info in self.vms.items():
            vm_process = vm_info.get('process', 'none')
            if vm_process in 'alive':
                logger.info(f"VM '{vm}' will be gracefully shut down...")
                running_vms.append(vm)
        with open('running_vms.pkl', 'wb') as f:
            pickle.dump(running_vms, f)
            logger.info("Pickle file with the VMs to start once host is started again was created.")
        for vm in running_vms:
            self.shutdown_vm(vm)
        

    def start_vms_at_host_startup(self):
        logger.info(f"Host is starting up, validating if pickle contains VMs to restart...")
        with open('running_vms.pkl', 'rb') as f:
            vms_to_restart = pickle.load(f)
        for vm in vms_to_restart:
            self.start_vm(vm)