import socket

class Connection:
    def __init__(self, socket):
        self._socket = socket

    def sendMsg(self, msg):
        """
        Send message to the client

        Sends message to the client using
        sendall to prevent short writes
        """
        # Send the length of the message first
        self._socket.sendall(len(msg).to_bytes(4, byteorder='big'))
        # Send the message
        self._socket.sendall(msg)

    def recvMsg(self):
        """
        Receive message from the client

        Receives message from the client,
        first the length of it and then it is made
        sure that the whole message is received to
        prevent short reads
        """
        # Receive the length of the message
        length_data = b''
        while len(length_data) < 4:
            length_data += self._socket.recv(4 - len(length_data))
        length = int.from_bytes(length_data, byteorder='big')
        # Receive the message
        data = b''
        while len(data) < length:
            data += self._socket.recv(length - len(data))
        return data
    
    def close(self):
        """
        Close connection

        Closes the socket connection to the client
        """
        if self._socket:
            self._socket.close()
            self._socket = None