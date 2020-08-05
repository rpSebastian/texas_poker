import pika
import sys

credentials = pika.PlainCredentials("root", "root")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="172.30.224.1",
        credentials=credentials,
        heartbeat=0
    ))

channel = connection.channel()


# channel.exchange_declare(exchange='logs', exchange_type='fanout')

# for i in range(10000):
#     message = 'info: Hello Wolddddddddddddddddddddddddddddddddddddddddddddd'
#     channel.basic_publish(exchange='logs', routing_key='', body=message)
#     # print('[x] Send {}'.format(message))
# connection.close()
