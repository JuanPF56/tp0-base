import logging
import signal

from common.acceptor import Acceptor
from common.client import Client
from common.utils import has_won, load_bets, store_bets

class Server:
    def __init__(self, port, listen_backlog, clients):
        """
        Server class
        
        Server class that accepts connections from clients and
        handles the communication with them
        """
        self.acceptor = Acceptor(port, listen_backlog)
        self.clients_to_await = clients
        self.is_running = True

        self.clients= {}

        # Register signal handler for SIGTERM signal
        signal.signal(signal.SIGTERM, self.__handle_sigterm)

    def __handle_sigterm(self, signum, frame):
        """
        Signal handler for SIGTERM signal
        
        When SIGTERM signal is received, server will stop accepting new
        connections and stop all the client connections
        """
        logging.info("SIGTERM received, stopping server")
        self.__stop_server()

    def run(self):
        """
        Server loop

        Server that accept new connections and establishes a
        communication with clients (one at a time), it handles the
        bets of each client and leaves its connection open until all 
        the clients are done, then it picks the winners and notifies
        them all
        """

        while self.is_running:
            try:
                # Accept new connections
                client_connection = self.acceptor.accept()
            except OSError as e:
                # If an error occurs, stop the server
                logging.error(f"action: accept_connections | result: fail | error: {e}")
                self.__stop_server()
                break
            if client_connection is not None:
                new_client = Client(client_connection)
                agency_id = new_client.getAgencyID()
                self.clients[agency_id] = new_client
                logging.debug(f"action: accept_connections | result: success | agency_id: {agency_id}")
                self.__handle_client_connection(agency_id)

                # Check if all the clients being awaited are done
                if len(self.clients) == self.clients_to_await and all(client.getDone() for client in self.clients.values()):
                    self.__handle_winners()
                    self.__stop_server()

            
    def __handle_client_connection(self, agency_id):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        last_batch = False
        client= self.clients[agency_id]
        logging.debug(f"action: apuesta_recibida | result: in_progress | client: {client.getAgencyID()}")
        try:
            while not last_batch:
                # Parse the message and store the bets
                bets, last_batch = client.receiveBatch()
                success = self._store_bet(bets)
                client.sendResponse(success)
        except OSError as e:
            logging.error(f"action: apuesta_recibida | result: fail | error: {e}")
        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | error: {e}")
            client.sendResponse(False)
        finally:
            # If all the bets were received, keep the connection open but mark the client as done
            client.setDone()


    def __handle_winners(self):
        """
        Handle winners

        Function that gets the winners from the storage file and sends
        the winners to all the clients
        """
        try:
            all_bets = load_bets()
            winners = {}
            for bet in all_bets:
                if has_won(bet):
                    winners[bet.agency].append(bet)
            for client in self.clients.values():
                client.sendWinners(winners.get(client.getAgencyID(), [])) 
            logging.info(f"action: sorteo | result: success")     
        except OSError as e:
            logging.error(f"action: sorteo | result: fail | error: {e}")      


    def _store_bet(self, bets):
        """
        Store the bets in the storage file

        Function stores the bets in the storage file and returns a boolean
        indicating if the operation was successful
        """
        try:
            store_bets(bets)
            logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
            return True
        except OSError as e:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
            return False
        
    def __stop_server(self):
        """
        Stop the server

        Function stops the server by closing the acceptor socket and
        all the client sockets
        """
        self.is_running = False
        logging.info("Closing acceptor connection")
        self.acceptor.close()
        logging.info("Closing client connections")
        for client in self.clients.values():
            client.close()