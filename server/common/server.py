import logging
import signal
import multiprocessing

from common.acceptor import Acceptor
from common.client import Client
from common.bethandler import BetHandler

class Server:
    def __init__(self, port, listen_backlog, clients):
        """
        Server class
        
        Server class that accepts connections from clients and
        handles the communication with them
        """
        self.acceptor = Acceptor(port, listen_backlog)
        self.bet_handler = None
        self.clients_to_await = clients
        self.is_running = True

        # Create a manager to handle shared queues
        self.manager = multiprocessing.Manager()

        self.clients = {}
        self.clients_queues = self.manager.dict()

        # Register signal handler for SIGTERM signal
        signal.signal(signal.SIGTERM, self.__handleSigterm)

    def __handleSigterm(self, signum, frame):
        """
        Signal handler for SIGTERM signal
        
        When SIGTERM signal is received, server will stop accepting new
        connections and stop all the client connections
        """
        logging.info("SIGTERM received, stopping server")
        self.__stopServer()

    def run(self):
        """
        Server loop

        Server that accepts new connections and establishes a
        communication with clients, handling each one in a separate
        process. It also starts a process to handle the bets.
        Client connections and bet processes are communicated through
        blocking queues.
        """

        # Create a queue for the bet handler
        bet_handler_queue = self.manager.Queue()
        # Start the bet handler process, passing both its queue and the
        # shared dictionary of client queues
        self.bet_handler = BetHandler(self.clients_to_await, bet_handler_queue, self.clients_queues)
        self.bet_handler.start()

        # This loop will run until the server is stopped,
        # in which case the resources will be closed/joined
        while self.is_running:
            try:
                # Accept new connections
                client_connection = self.acceptor.accept()
                if client_connection is not None:
                    # Create a new client process
                    new_client = Client(client_connection, bet_handler_queue, new_client_queue)
                    agency_id = new_client.getAgencyID()
                    # Create a new queue for the client
                    new_client_queue = self.manager.Queue()
                    # Register the client and its queue in the dictionaries
                    self.clients[agency_id] = new_client
                    self.clients_queues[agency_id] = new_client_queue
                    logging.debug(f"action: aceptar_conexion | result: success | agency_id: {agency_id}")
                    # Start the client process
                    new_client.start()
            except OSError as e:
                # If an error occurs, stop the server
                logging.error(f"action: aceptar_conexion | result: fail | error: {e}")
                self.__stopServer()
                break
        
    def __stopServer(self):
        """
        Stop the server

        Function stops the server by closing the acceptor socket,
        all the client sockets and joining all the client processes
        and the bet handler process.

        It should be safe to call this function multiple times,
        the resources will be closed only once
        """
        self.is_running = False
        logging.info("Closing acceptor connection")
        self.acceptor.close()
        logging.info("Closing client connections")
        for client in self.clients.values():
            client.close()
            client.join()
        logging.info("Stopping bet handler")
        self.bet_handler.join()
        self.manager.shutdown()