import socket
import logging

from common.connection import Connection

class Acceptor:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

    def accept(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
        except OSError as e:
            # If server socket was closed, return None
            return None

        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return Connection(c)
    
    def close(self):
        """
        Close server socket
        
        Function closes the server socket
        """
        self._server_socket.close()
