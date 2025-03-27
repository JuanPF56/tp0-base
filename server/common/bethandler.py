
import logging
import multiprocessing

from common.utils import has_won, load_bets, store_bets

class BetHandler(multiprocessing.Process):
    def __init__(self, clients_to_await, queue, client_queues):
        """
        BetHandler class

        This class is a process that handles the bets received from the clients
        and stores them in a file. It also handles the winners and sends them
        back to the clients.
        """
        super().__init__()
        self.clients_to_await = clients_to_await
        self.queue = queue
        self.joined = False 

        self.clients = client_queues
        self.finished_clients = {}

    def run(self):
        """
        Run the bet handler process

        This method will run until the server is stopped, in which case
        the resources will be closed/joined
        """
        while not self.joined:
            try:
                # Wait for messages from the clients
                message = self.queue.get()
                if message[0] == "BETS":
                    agency_id, bets, last_batch = message[1], message[2], message[3]
                    self.__handleBets(agency_id, bets, last_batch)
                elif message[0] == "CLIENT_DISCONNECT":
                    agency_id = message[1]
                    self.__handleClientDisconnect(agency_id)
            except Exception as e:
                # If an error occurs, stop the server
                logging.error(f"action: procesar_apuesta | result: fail | error: {e}")
                break

    def getQueue(self):
        """
        Get the queue of the bet handler
        """
        return self.queue

    def __handleBets(self, agency_id, bets, last_batch):
        """
        Handle incoming bets from clients

        Function that handles the incoming bets from the clients and
        stores them in the storage file. It also handles the last batch
        of bets and sends confirmations to the client.
        """
        logging.debug(f"action: procesar_apuesta | result: in_progress | agency_id: {agency_id} | cantidad: {len(bets)}")
        if self.__storeBet(bets):
            # Return confirmation to the client
            self.clients[agency_id].put(True)
            # If the last batch is received, mark the client as done
            if last_batch:
                self.finished_clients[agency_id] = True
                # Check if all clients are done
                if len(self.finished_clients) == self.clients_to_await and all(client for client in self.finished_clients.values()):
                    self.__handleWinners()
        else:
            # Return failure to the client
            self.clients[agency_id].put(False)

    def __handleClientDisconnect(self, agency_id):
        """
        Handle client disconnect
        Function that handles the disconnection of a client and
        removes it from the list of clients
        """
        if agency_id in self.clients.keys():
            del self.clients[agency_id]
            logging.info(f"action: cliente_desconectado | result: success | agency_id: {agency_id}")
        else:
            logging.warning(f"action: cliente_desconectado | result: fail | agency_id: {agency_id} not found")
    
    def __handleWinners(self):
        """
        Handle winners

        Function that gets the winners from the storage file and sends
        the winners to all the clients
        """
        try:
            all_bets = load_bets()
            winners = {}
            for id in self.clients.keys():
                winners[id] = []
            for bet in all_bets:
                if has_won(bet):
                    winners[bet.agency].append(bet)
            for id, client in self.clients.items():
                # Send winners to the client
                client.put(winners.get(id, []))
            logging.info(f"action: sorteo | result: success")     
        except OSError as e:
            logging.error(f"action: sorteo | result: fail | error: {e}")      

    def __storeBet(self, bets):
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

    def join(self):
        """
        Join process
        """
        if not self.joined:
            self.joined = True
            super().join()