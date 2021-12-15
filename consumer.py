import json
import os
from pathlib import Path
import pika
import subprocess
import sys
import uuid


QUEUE_NAME = 'vm-queue'
BASE_IMAGE_FOLDER = Path('base_images')
USER_IMAGE_FOLDER = Path('user_images')

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)


class QemuException(Exception):
    pass


def create_user_image(vm_id: str, image_name: str) -> Path:
    base_image = BASE_IMAGE_FOLDER / f'{image_name}.qcow2'
    if not base_image.is_file():
        raise IOError(f'Image "{image_name}" does not exist')

    user_image = USER_IMAGE_FOLDER / f'{vm_id}.qcow2'

    create_img_result = subprocess.run([
        'qemu-img', 'create', '-f', 'qcow2',
        '-b', str(base_image.absolute()), '-F', 'qcow2', str(user_image)])
    if create_img_result.returncode != 0:
        raise QemuException(f'Could not create image for VM "{vm_id}"')

    return user_image


def callback(ch, method, properties, body):
    message = body.decode('utf-8')
    print('Received message: ' + message)

    data = json.loads(message)
    if 'command' in data and data['command'] == 'start-vm':
        vm_id = str(uuid.uuid4())
        print(f'Starting VM "{vm_id}"')

        try:
            image_name = os.path.basename(data['options']['image'])
        except KeyError:
            print('Image not specified', file=sys.stderr)
            return

        try:
            user_image = create_user_image(vm_id, image_name)
        except (OSError, QemuException) as e:
            print(str(e), file=sys.stderr)
            return

        p = subprocess.Popen([
            'qemu-system-x86_64', '-m', '4096', '-hda', str(user_image)])
        print(f'Started VM "{vm_id}" as process ID {p.pid}')

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

channel.start_consuming()