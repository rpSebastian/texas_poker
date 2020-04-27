import sys
import pika
import uuid

class RpcClient():
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='rpc_queue')
        self.call_back_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue        
        self.channel.basic_consume(queue=self.call_back_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def __call__(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='', 
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.call_back_queue,
                correlation_id=self.corr_id),
            body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)


print(RpcClient()(int(sys.argv[1])))
