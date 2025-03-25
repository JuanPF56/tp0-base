import logging
from common.utils import Bet

"""
Protocol class

This class is responsible for parsing the messages received from the client
and creating the responses.

The messages are expected to follow a TLV (Type, Length, Value) format where
each field is indicated by a type byte, a length byte and the value itself.

    * TLV (Type, Length, Value) format
        * Type: 1 byte
        * Length: 1 byte
        * Value: n bytes

    * 0x01: Integer (4 bytes)
 	* 0x02: String (n bytes)
	* 0x03: Character (1 byte)
	* 0x04: Bet (n bytes, composed of the following fields)
		* 0x01: Agency ID
		* 0x02: Name
		* 0x03: Surname
		* 0x04: DNI
		* 0x05: Birthdate
		* 0x06: Number
"""
class Protocol:
    def __init__(self):
        pass

    def parseBetMessage(self, message):
        """
        Parse the message received from the client

        The message is expected to follow the TLV format indicated in the
        class description. The fields can arrive in any order, but they
        are expected to be all present.
        """

        # Check that the message is of type Bet
        if message[0] != 0x04:
            raise ValueError("invalid message type, expected Bet")
        # Get message length
        total_length = message[1]

        # Parse the message
        fields = {}
        length = 0
        start = 2
        while start < len(message):
            field_type, field_value, field_length = self._get_next_field(message, start)
            fields[field_type] = field_value
            length += field_length
            start += 2 + field_length

        if len(fields) != 6 or length != total_length:
            raise ValueError("invalid message format")
        
        try:
            return Bet(fields[0x01], fields[0x02], fields[0x03], fields[0x04], fields[0x05], fields[0x06])
        except KeyError:
            raise ValueError("missing fields in Bet message")

    def _get_next_field(self, message, start):
        """
        Get the next field from the message

        The field is expected to follow the TLV format indicated in the
        class description.
        """
        # Get field type
        field_type = message[start]
        # Get field length
        field_length = message[start + 1]
        # Get field value
        field_value = message[start + 2:start + 2 + field_length]
    
        if field_type == 0x01 or field_type == 0x04 or field_type == 0x06:
            field_value = int.from_bytes(field_value, byteorder='big')
        else:
            field_value = field_value.decode('utf-8')
        return field_type, field_value, field_length
    
    def createResponse(self, success):
        """
        Create a response message to be sent to the client

        The response message uses TLV format with a single field of type
        0x03 (Character) indicating the result of the operation.
        
        This is trivial now and could be done without the TLV format,
        but it's done so it can easily be extended in the future to
        handle more information.
        
	    TODO: Handle more complex responses in future iterations
        """
        return bytes([0x03, 0x01, 0x01 if success else 0x00])
