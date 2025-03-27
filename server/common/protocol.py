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
        * Length: 1 byte (or 2 bytes for Batch type)
        * Value: n bytes

    * Protocol types:
        * 0x01: Batch (n bytes, max 65535, composed of the following fields)
            * 0x01: Amount of bets (uint32, 4 bytes)
            * 0x02: Bet (n bytes as defined above, could be multiple)
            * 0x03: Agency ID (uint32, 4 bytes)
            * 0x04: Last batch flag (1 byte)
        * 0x02: Bet (n bytes, composed of the following fields)
            * 0x01: Name (string, n bytes, max 255)
            * 0x02: Surname (string, n bytes, max 255)
            * 0x03: DNI (uint32, 4 bytes)
            * 0x04: Birthdate (string, n bytes, max 255)
            * 0x05: Number (uint32, 4 bytes)
        * 0x03: Response (1 byte)
"""
class Protocol:
    def __init__(self):
        pass

    def parseBatchMessage(self, message):
        """
        Parse the batch message

        The batch is expected to follow the TLV format indicated in the
        class description. There could be multiple bets, the message is 
        expected to contain at least one. For simplicity, it is expected
        that the fields are in the correct order:
            
            * Amount of bets
            * Bet 1
            * Bet 2
            * ...
            * Bet n
            * Agency ID
            * Last batch flag

        """

        logging.debug(f"action: apuesta_recibida | result: in_progress | message: {message}")

        length = 0
        # Check that the message is of type Batch
        if message[0] != 0x01:
            raise ValueError("invalid message type, expected Batch")
        # Get message length (2 bytes)
        total_length = int.from_bytes(message[1:3], byteorder='big')

        # Check that the amount of bets is next
        if message[3] != 0x01:
            raise ValueError("invalid message format, expected amount of bets first")
        # Check that the amount of bets is 4 bytes
        if message[4] != 4:
            raise ValueError("invalid message format, expected 4 bytes for amount of bets")
        # Get the amount of bets
        amount_of_bets = int.from_bytes(message[5:9], byteorder='big')
        length += 4

        # Check that the bets are next
        if message[9] != 0x02:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("invalid message format, expected bets")

        bets = []
        current_byte = 9
        # Parse all the bets
        while message[current_byte] == 0x02:
            current_byte += 1
            bet_length = message[current_byte]
            current_byte += 1
            length += bet_length
            # Parse the bet and get the next byte to parse
            bet, current_byte = self._parseBet(message, current_byte, bet_length, amount_of_bets)
            bets.append(bet)
        
        # Check that the agency ID is next
        if message[current_byte] != 0x03:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("invalid message format, expected agency ID")
        # Check that the agency ID is 4 bytes
        if message[current_byte + 1] != 4:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("invalid message format, expected 4 bytes for agency ID")
        # Get the agency ID
        agency_id = int.from_bytes(message[current_byte + 2:current_byte + 6], byteorder='big')
        length += 4        

        # Add the agency ID to the bets
        for bet in bets:
            bet.agency = agency_id

        # Check that the last batch flag is next
        if message[current_byte + 6] != 0x04:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("invalid message format, expected last batch flag")
        # Check that the last batch flag is 1 byte
        if message[current_byte + 7] != 1:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("invalid message format, expected 1 byte for last batch flag")
        # Get the last batch flag
        last_batch = message[current_byte + 8]
        length += 1

        # Check that the total length of the message is correct
        if length != total_length:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("invalid message format, incorrect length")
        
        return bets, last_batch     


    def _parseBet(self, message, current_byte, total_length, amount_of_bets):
        """
        Parse the bet message

        The bet is expected to follow the TLV format indicated in the
        class description.
        """

        fields = {}
        start = current_byte
        length = 0

        #logging.debug(f"action: apuesta_recibida | result: in_progress | current_byte: {current_byte} | total_length: {total_length}")

        # Parse all the fields
        while start < current_byte + total_length + 10:
            field_type, field_value, field_length = self._get_next_bet_field(message, start)
            fields[field_type] = field_value# Add the length of the field's value
            length += field_length
            # Move to the next field
            start += 2 + field_length

        #logging.debug(f"action: apuesta_recibida | result: in_progress | fields: {fields}")

        # Check that all the fields are present
        if len(fields) != 5 or length != total_length:
            raise ValueError("invalid message format")
        
        try:
            # Return the bet with placeholder agency 0 (will be replaced later by the actual agency
            # ID sent in the batch message)
            return (Bet(0,fields[0x01], fields[0x02], fields[0x03], fields[0x04], fields[0x05]), start)
        except KeyError:
            logging.error(f"action: apuesta_recibida | result: fail | cantidad: {amount_of_bets}")
            raise ValueError("missing fields in Bet message")

    def _get_next_bet_field(self, message, start):
        """
        Get the next field from the bet

        The field is expected to follow the TLV format indicated in the
        class description.
        """
        # Get field type
        field_type = message[start]
        # Get field length
        field_length = message[start + 1]
        # Get field value
        field_value = message[start + 2:start + 2 + field_length]
    
        if field_type == 0x03 or field_type == 0x05:
            field_value = int.from_bytes(field_value, byteorder='big')
        else:
            field_value = field_value.decode('utf-8')
        return field_type, field_value, field_length
    
    def createResponse(self, success):
        """
        Create a response message to be sent to the client

        The response message uses TLV format with a single field of type
        0x02 indicating the result of the operation.
        
        This is trivial now and could be done without the TLV format,
        but it's done so it can easily be extended in the future to
        handle more information.
        
	    TODO: Handle more complex responses in future iterations
        """
        return bytes([0x03, 0x01, 0x01 if success else 0x00])
