import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


severities = sys.argv[1:]

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
for severity in severities:
    channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=severity)

channel.basic_consume(queue=queue_name,
                        auto_5ack=True,
                        uu7ib=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
