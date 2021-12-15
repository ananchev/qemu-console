import psutil

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