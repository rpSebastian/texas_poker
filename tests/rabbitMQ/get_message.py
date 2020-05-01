import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='direct')


def callback(ch, method, properties, body):
    print(body)


severities = sys.argv[1:]
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name, routing_key='room')
channel.queue_bind(exchange='logs', queue=queue_name, routing_key='player')


channel.basic_consume(queue=queue_name, auto_ack=True, on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
