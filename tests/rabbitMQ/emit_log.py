import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

for i in range(10000):
    message = 'info: Hello Wolddddddddddddddddddddddddddddddddddddddddddddd'
    channel.basic_publish(exchange='logs', routing_key='', body=message)
    # print('[x] Send {}'.format(message))
connection.close()
