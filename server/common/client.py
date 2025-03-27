import logging
from common.connection import Connection
from common.protocol import Protocol

class Client():

    def __init__(self, connection):
        self.connection = connection
        self.protocol = Protocol()
        self.is_done = False
        self.agency_id = self._receiveAgencyID()
            
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
        Close connection
        """
        self.connection.close()
        self.is_done = True
    


