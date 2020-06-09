import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pika
from config import cfg
import threading
import time
import multiprocessing
from logs import logger

class Rabbitmq():
    def __init__(self):
        credentials = pika.PlainCredentials(cfg["rabbitMQ"]["username"], cfg["rabbitMQ"]["password"])
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg["rabbitMQ"]["host"], credentials=credentials, heartbeat=0))
        self.channel = self.connection.channel()
        self.clean_channel = self.connection.channel()

    def recv_msg_from_queue(self, queue_name, callback):
        self.queue_declare(queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    def recv_msg_from_fanout_exchange(self, queue_name, exchange_name, callback):
        self.exchange_declare(exchange_name, "fanout")
        self.queue_declare(queue_name)
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    def recv_msg_from_direct_exchange(self, queue_name, exchange_name, routing_key, callback):
        self.exchange_declare(exchange_name, 'direct')
        self.queue_declare(queue_name)
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    def send_msg_to_queue(self, queue_name, data):
        self.channel.basic_publish(exchange='', routing_key=queue_name, body=data)

    def send_msg_to_exchange(self, exchange_name, routing_key, data):
        assert len(exchange_name) > 2 
        self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=data)

    def queue_declare(self, queue_name):
        self.channel.queue_declare(queue=queue_name)
        self.clean(queue_name)

    def exchange_declare(self, exchange_name, exchange_type):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

    def start(self):
        self.channel.start_consuming()

    def clean(self, queue_name):
        def clean_func(queue_name):
            def callback(ch, method, props, body):
                pass
                # print("inner", body)
            credentials = pika.PlainCredentials(cfg["rabbitMQ"]["username"], cfg["rabbitMQ"]["password"])
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg["rabbitMQ"]["host"], credentials=credentials, heartbeat=0))
            channel = connection.channel()
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        t = multiprocessing.Process(target=clean_func, args=(queue_name, ))
        t.start()
        time.sleep(0.1)
        # 不加-9 或者 t.terminate() 无法杀死用线程开启的进程 未知原因
        os.system("kill -9 {}".format(t.pid))
