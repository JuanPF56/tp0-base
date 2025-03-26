package common

import (
	"encoding/binary"
	"fmt"
)

// Protocol Entity
type Protocol struct {
	id int
}

/*
 * Protocol definition:

 * TLV (Type, Length, Value) format
	* Type: 1 byte
	* Length: 1 byte (or 2 bytes for Batch type)
	* Value: n bytes

 * Protocol types:
	* 0x01: Bet (n bytes, composed of the following fields)
		* 0x01: Name (string, n bytes, max 255)
		* 0x02: Surname (string, n bytes, max 255)
		* 0x03: DNI (uint32, 4 bytes)
		* 0x04: Birthdate (string, n bytes, max 255)
		* 0x05: Number (uint32, 4 bytes)
	* 0x02: Response (1 byte)
	* 0x03: Batch (n bytes, max 65535, composed of the following fields)
		* 0x01: Bet (n bytes as defined above, could be multiple)
		* 0x02: Agency ID (uint32, 4 bytes)
		* 0x03: Last batch flag (1 byte)
*/

// CreateBetBatchMessage: Creates a batch message with the given list of bets and EOF flag using TLV (type, length, value) format
func (p *Protocol) CreateBetBatchMessage(bets []Bet, eof bool) []byte {
	// Create the message as a byte slice
	msg := make([]byte, 0)
	serializedBets := make([]byte, 0)
	// Start the length at 5 (4 bytes for the agency ID and 1 byte for the last batch flag)
	length := 5
	for _, bet := range bets {
		// Calculate the length of the bet message
		length += len(bet.Name) + len(bet.Surname) + len(bet.Birthdate) + 8
		// Create the bet message
		betMsg := p.CreateBetMessage(bet.Name, bet.Surname, bet.DNI, bet.Birthdate, bet.Number)
		// Append the bet message
		serializedBets = append(serializedBets, betMsg...)
	}

	// Append the TLV fields

	// Type (Batch)
	msg = append(msg, 0x03)
	lengthBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(lengthBytes, uint16(length))
	msg = append(msg, lengthBytes...)

	// Bets (append all the serialized bets)
	msg = append(msg, serializedBets...)

	// Agency ID (4 bytes)
	agencyID := make([]byte, 4)
	binary.BigEndian.PutUint32(agencyID, uint32(p.id))
	msg = append(msg, 0x02)
	msg = append(msg, 4)
	msg = append(msg, agencyID...)

	// Last batch flag (1 byte)
	flag := byte(0)
	if eof {
		flag = 1
	}
	msg = append(msg, 0x03)
	msg = append(msg, 1)
	msg = append(msg, flag)

	return msg
}

// CreateBetMessage: Creates a bet message with the given parameters using TLV (type, length, value) format
func (p *Protocol) CreateBetMessage(
	name string,
	surname string,
	dni int,
	birthdate string,
	number int) []byte {
	// Create the message as a byte slice
	msg := make([]byte, 0)
	length := len(name) + len(surname) + len(birthdate) + 8

	// Append the TLV fields

	// Type (Bet)
	msg = append(msg, 0x01)
	msg = append(msg, byte(length))

	// Name
	msg = append(msg, 0x01)
	msg = append(msg, byte(len(name)))
	msg = append(msg, []byte(name)...)

	// Surname
	msg = append(msg, 0x02)
	msg = append(msg, byte(len(surname)))
	msg = append(msg, []byte(surname)...)

	// DNI
	msg = append(msg, 0x03)
	dniBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(dniBytes, uint32(dni))
	msg = append(msg, byte(len(dniBytes)))
	msg = append(msg, dniBytes...)

	// Birthdate
	msg = append(msg, 0x04)
	msg = append(msg, byte(len(birthdate)))
	msg = append(msg, []byte(birthdate)...)

	// Number
	msg = append(msg, 0x05)
	numberBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(numberBytes, uint32(number))
	msg = append(msg, byte(len(numberBytes)))
	msg = append(msg, numberBytes...)

	return msg
}

// ParseResponse: Parses the response message and returns the result
func (p *Protocol) ParseResponse(msg []byte) (string, error) {
	// The response will use the TLV format but its value will be a single byte long
	// This is trivial now and could be done without the TLV format, but it's done so it
	// can easily be extended in the future to handle more information.
	if len(msg) != 3 {
		return "", fmt.Errorf("invalid response message")
	}

	// Check the type (should be response)
	if msg[0] != 0x02 {
		return "", fmt.Errorf("invalid response type")
	}

	// Check the length (should be 1)
	if msg[1] != 1 {
		return "", fmt.Errorf("invalid response length")
	}

	response := "success"

	// Check the value (0 for failure, 1 for success)
	if msg[2] != 1 {
		response = "fail"
	}

	return response, nil
}
