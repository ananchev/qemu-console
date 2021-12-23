import os, psutil
from configparser import ConfigParser
import qemu.qmp as qmp

# Establish logging
from libs.logger import logger
logger = logger.getChild('console')




class QEMUConsole():

    vms={} # dict with all managed vms and their status info

    def __init__(self) -> None:
        # Load the application configuration
        logger.info("QEMUConsole class initialised.")
        self.conf = ConfigParser()
        self.conf.read('config.ini')
        self.fetch_running_vms()


    def _managed_vm_names(self):
        return os.listdir(self.conf['Locations']['vms'])



    def fetch_running_vms(self):
        managed_vm_names = self._managed_vm_names()

        live_qemu_vm_names = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline','username']):
            if 'qemu' in proc.name():
                if '-name' in proc.info['cmdline']:
                    name_flag_position = proc.info['cmdline'].index('-name')
                    name = proc.info['cmdline'][name_flag_position+1] # vm name is what stays after the -name flag
                    live_qemu_vm_names.append(name)
            
        # write statuses
        for vm in managed_vm_names:
            if vm in live_qemu_vm_names:
                self.vms[vm] = {"process":"alive"} 
                self._fetch_vm_status(vm)
            else:
                self.vms[vm] = {"process":"not running"} 



    def is_vm_process_running(self, vm_name):
        vm_info = self.vms.get(vm_name, None)
        if vm_info['process'] in "alive":
            return True
        return False



    def _fetch_vm_status(self, vm_name):
        retval = self.execute_QMP_command(vm_name, command='query-status')

        # retval comes as {'return': {'status': 'paused', 'singlestep': False, 'running': False}}
        vm_status = retval['return']['status']
        self.vms[vm_name]['status']=vm_status


    
    def execute_QMP_command(self, vm_name, command, command_arguments={}):
        if not self.is_vm_process_running(vm_name):
            logger.info(f"QEMU process for '{vm_name}' is not running")
            return None
        monitor = qmp.QEMUMonitorProtocol(address=f"{self.conf['Locations']['sockets']}/{vm_name}.sock")
        monitor.connect()
        msg = {'execute': command,
               'arguments': command_arguments}
        retval = monitor.cmd_obj(qmp_cmd=msg)
        monitor.close
        return retval