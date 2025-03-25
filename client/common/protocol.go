package common

import (
	"encoding/binary"
	"fmt"
)

// Protocol Entity
type Protocol struct{}

/*
 * Protocol definition:

 * TLV (Type, Length, Value) format
	* Type: 1 byte
	* Length: 1 byte
	* Value: n bytes

 * Protocol types:
 	* 0x01: Integer (4 bytes)
 	* 0x02: String (n bytes)
	* 0x03: Character (1 byte)
*/

// CreateBetMessage: Creates a bet message with the given parameters using TLV (type, length, value) format
func (p *Protocol) CreateBetMessage(
	name string,
	surname string,
	dni int,
	birthdate string,
	number int) []byte {
	// Create the message as a byte slice
	msg := make([]byte, 0)

	// Append the TLV fields

	// Name
	msg = append(msg, 0x02)
	msg = append(msg, byte(len(name)))
	msg = append(msg, []byte(name)...)

	// Surname
	msg = append(msg, 0x02)
	msg = append(msg, byte(len(surname)))
	msg = append(msg, []byte(surname)...)

	// DNI
	msg = append(msg, 0x01)
	dniBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(dniBytes, uint32(dni))
	msg = append(msg, byte(len(dniBytes)))
	msg = append(msg, dniBytes...)

	// Birthdate
	msg = append(msg, 0x02)
	msg = append(msg, byte(len(birthdate)))
	msg = append(msg, []byte(birthdate)...)

	// Number
	msg = append(msg, 0x01)
	numberBytes := make([]byte, 4)
	binary.BigEndian.PutUint32(numberBytes, uint32(number))
	msg = append(msg, byte(len(numberBytes)))
	msg = append(msg, numberBytes...)

	return msg
}

// ParseResponse: Parses the response message and returns the result
func (p *Protocol) ParseResponse(msg []byte) (string, error) {
	// The response will use the TLV format but should only be one field of type character
	// This is trivial now and could be done without the TLV format, but it's done so it
	// can easily be extended in the future to handle more information.
	// TODO: Handle more complex responses in future iterations
	if len(msg) != 3 {
		return "", fmt.Errorf("invalid response message")
	}

	// Check the type (should be character)
	if msg[0] != 0x03 {
		return "", fmt.Errorf("invalid response type")
	}

	// Check the length (should be 1)
	if msg[1] != 1 {
		return "", fmt.Errorf("invalid response length")
	}

	response := "OK"

	// Check the value (0 for success, 1 for failure)
	if msg[2] != 0 {
		response = "FAIL"
	}

	return response, nil
}
