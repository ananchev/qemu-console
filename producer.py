import pika
import json

QUEUE_NAME = 'vm-queue'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)

message = json.dumps({
    'command': 'start-vm',
    'options': {
        'image': 'ubuntu_base',
    }
})
channel.basic_publish(
    exchange='', routing_key=QUEUE_NAME, body=message)