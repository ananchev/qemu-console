import traceback
import psutil
def fetch_running_vms():
    qemu_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline','username']):
        if 'qemu' in proc.name():
            qemu_processes.append(proc.info)

    for p in qemu_processes:
        if not '-name' in p['cmdline']:
            # no name argument supplied when starting the VM - should be only for the VM docker desktop runs
            continue 
        name_flag_position = p['cmdline'].index('-name')
        name = p['cmdline'][name_flag_position+1]
        print (name)

import qemu.qmp as qmp
import json
def qmp_test():
    monitor = qmp.QEMUMonitorProtocol(address='/tmp/manjaro.sock')
    monitor.connect()

    # # show all supported commands
    # msg = { "execute": "query-commands" }
    # r = monitor.cmd_obj(qmp_cmd=msg)
    # with open('qemu-commands.json', 'w', encoding='utf-8') as f:
    #     json.dump(r, f, ensure_ascii=False, indent=4)

    # msg = {'execute': 'query-status'}
    # msg = {'execute': 'cont'}
    # msg = {'execute': 'stop'}   #{'return': {'status': 'paused', 'singlestep': False, 'running': False}}
    # msg = {'execute': 'system_powerdown'}
    msg = {
        'execute': 'query-block-jobs'
    }   
    # msg = {
    #     "execute": "block-job-cancel",
    #     "arguments": {
    #     "device": "job-bckp-manjaro"
    #     } 
    # }
    r = monitor.cmd_obj(qmp_cmd=msg)
    print(r)


def parse():
    str = {'return': [{'auto-finalize': True, 'io-status': 'ok', 'device': 'job-bckp-manjaro', 'auto-dismiss': True, 'busy': True, 'len': 9137881088, 'offset': 2574450688, 'status': 'running', 'paused': False, 'speed': 0, 'ready': False, 'type': 'mirror'}]}
    # res_json = json.loads(str)
    ret = str['return'][0]['ready']
    print (ret)

import subprocess
def process():
    command = ['/bin/ls', '-G', '-l', '/Users/ananchev']
    process = subprocess.run(command,
                         stdout=subprocess.PIPE, 
                         universal_newlines=True)
    print(process.stdout)

if __name__ == '__main__':
    try:
        parse()
    except Exception as e:
        traceback.print_exc()