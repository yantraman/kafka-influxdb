import unittest
from mock import Mock
import random
from kafka_influxdb.worker import Worker
from kafka_influxdb.encoder import echo_encoder


class Config:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.kafka_topic = "test"
        self.influxdb_dbname = "mydb"


class DummyReader(object):
    """
    A reader that yields dummy messages
    """
    def __init__(self, messages, num_messages):
        self.messages = messages
        self.num_messages = num_messages

    def read(self):
        for i in range(self.num_messages):
            yield random.choice(self.messages)


class DummyWriter(object):
    """
    A fake writer that does nothing with the input data
    """
    def __init__(self):
        pass

    def write(self):
        pass


class TestKafkaInfluxDB(unittest.TestCase):
    def setUp(self):
        self.config = Config(100)
        self.encoder = echo_encoder.Encoder()
        self.writer = DummyWriter()
        self.writer = Mock()
        self.writer.write.return_value = True

    def test_buffering(self):
        self.reader = DummyReader(["myhost.load.load.shortterm 0.05 1436357630"], self.config.buffer_size - 1)
        self.client = Worker(self.reader, self.encoder, self.writer, self.config)
        self.client.consume()
        self.assertFalse(self.writer.write.called)

    def test_flush(self):
        self.reader = DummyReader(["myhost.load.load.shortterm 0.05 1436357630"], self.config.buffer_size)
        self.client = Worker(self.reader, self.encoder, self.writer, self.config)
        self.client.consume()
        self.assertTrue(self.writer.write.called)
