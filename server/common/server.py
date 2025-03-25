import logging
import signal

from common.acceptor import Acceptor
from common.protocol import Protocol
from common.utils import store_bets

class Server:
    def __init__(self, port, listen_backlog):
        self.acceptor = Acceptor(port, listen_backlog)
        self.protocol = Protocol()
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

    def __handle_client_connection(self, client_connection):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            bet = self.protocol.parseBetMessage(client_connection.recvMsg())
            success = self._store_bet(bet)
            client_connection.sendMsg(self.protocol.createResponse(success))
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        except ValueError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            client_connection.sendMsg(self.protocol.createResponse(False))
        finally:
            client_connection.close()


    def _store_bet(self, bet):
        """
        Store the bet in the storage file

        Function stores the bet in the storage file and returns a boolean
        indicating if the operation was successful
        """
        try:
            store_bets([bet])
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            return True
        except OSError as e:
            logging.error(f"action: apuesta_almacenada | result: fail | error: {e}")
            return False