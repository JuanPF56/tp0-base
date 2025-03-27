import logging
from common.protocol import Protocol
import multiprocessing

class Client(multiprocessing.Process):
    def __init__(self, connection, queue):
        """
        Client class

        This class is a process that handles the communication with a client
        """
        self.connection = connection
        self.protocol = Protocol()
        self.is_done = False
        self.agency_id = self._receiveAgencyID()
        self.bet_handler_queue = queue
        self.queue = multiprocessing.Queue()
        self.joined = False

        # Send agency ID and queue to the bet handler
        self.bet_handler_queue.put((self.agency_id, self.queue))

    def run(self):
        """
        Run the client process

        Read incoming messages from the socket, parse them and send
        them to the bet handler. The client process will run until it
        receives the winners from the bet handler, sending them to the
        client.
        """
        last_batch = False
        try:
            # Receive batches of bets from the client until the last batch
            while not last_batch:
                # Parse the message and send it to the bet handler
                bets, last_batch = self.receiveBatch()
                self.bet_handler_queue.put((self.agency_id, bets, last_batch))
                # Wait for confirmation from the bet handler
                success = self.queue.get()
                self.sendResponse(success)
            # If the last batch was correctly stored, wait for the winners
            winners = self.queue.get()
            self.sendWinners(winners)
        except OSError as e:
            logging.error(f"action: apuesta_recibida | result: fail | error: {e}")
        except ValueError as e:
            logging.error(f"action: apuesta_recibida | result: fail | error: {e}")
            self.sendResponse(False)
        finally:
            self.close()
            
    def _receiveAgencyID(self):
        """
        Receive agency ID from the client
        """
        return self.protocol.parseAgencyID(self.connection.recvMsg())

    def receiveBatch(self):
        """
        Receive batch of bets from the client
        """
        return self.protocol.parseBatchMessage(self.connection.recvMsg())
    
    def sendResponse(self, success):
        """
        Send response to the client
        """
        self.connection.sendMsg(self.protocol.createResponse(success))

    def sendWinners(self, winners):
        """
        Send winners to the client
        """
        self.connection.sendMsg(self.protocol.createWinners(winners))

    def getDone(self):
        """
        Get done status
        """
        return self.is_done
    
    def setDone(self):
        """
        Set done status
        """
        self.is_done = True

    def getAgencyID(self):
        """
        Get agency ID
        """
        return self.agency_id

    def close(self):
        """
        Close connection and queue
        """
        self.connection.close()
        self.is_done = True
        # Send termination signal to the bet handler (None)
        # to indicate that the client is done
        if self.queue:
            self.bet_handler_queue.put((self.agency_id, None, None))
            # Close the queue
            self.queue.close()
            self.queue = None
    def join(self):
        """
        Join process
        """
        self.joined = True
        super().join()
    


