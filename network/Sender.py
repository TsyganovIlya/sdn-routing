import socket


class Sender(object):

    def __init__(self, logger):
        self.logger = logger

    def send_islands(self, islands_in_bytes):
        sender = socket.socket()
        try:
            sender.connect(('127.0.0.1', 6111))
            sender.send(b'Islands:' + islands_in_bytes)
        except socket.error as e:
            self.logger.debug('Caught exception socket.error: {0}'.format(e))
        finally:
            sender.close()

    def send_path(self, path_in_bytes):
        sender = socket.socket()
        try:
            sender.connect(('127.0.0.1', 6111))
            sender.send(b'Path:' + path_in_bytes)
        except socket.error as e:
            self.logger.debug('Caught exception socket.error: {0}'.format(e))
        finally:
            sender.close()

    def send_paths(self, paths_in_bytes):
        sender = socket.socket()
        try:
            sender.connect(('127.0.0.1', 6111))
            sender.send(b'Paths:' + paths_in_bytes)
        except socket.error as e:
            self.logger.debug('Caught exception socket.error: {0}'.format(e))
        finally:
            sender.close()
