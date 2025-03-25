import logging
import signal

from common.acceptor import Acceptor

class Server:
    def __init__(self, port, listen_backlog):
        self.acceptor = Acceptor(port, listen_backlog)
        self.is_running = True

        # Register signal handler for SIGTERM signal
        signal.signal(signal.SIGTERM, self.__handle_sigterm)

    def __handle_sigterm(self, signum, frame):
        """
        Signal handler for SIGTERM signal
        
        When SIGTERM signal is received, server will stop accepting new
        connections and will finish the current connections before
        exiting
        """
        logging.info("SIGTERM received, stopping server")
        self.is_running = False
        logging.info("Closing acceptor connection")
        self.acceptor.close()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self.is_running:
            client_connection = self.acceptor.accept()
            if client_connection is not None:
                self.__handle_client_connection(client_connection)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

