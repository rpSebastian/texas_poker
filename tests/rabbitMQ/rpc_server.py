import pika


def fib(n):
    if n == 0 or n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


class RpcServer():
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.channel.basic_consume(queue='rpc_queue', on_message_callback=self.callback)

    def callback(self, ch, method, props, body):
        print(" [x] Received %r" % body)
        n = int(body)
        result = fib(n)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(result))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()


RpcServer().start()
