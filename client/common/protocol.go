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
 	* 0x01: Name
 	* 0x02: Surname
 	* 0x03: DNI
 	* 0x04: Birthdate
 	* 0x05: Number
	* 0x06: Response

 * Response values:
 	* 0x00: OK
	* 0x01: Error
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
	// Check if the message has at least 3 bytes
	if len(msg) < 3 {
		return "", fmt.Errorf("invalid response")
	}

	// Check the type of the message
	switch msg[0] {
	case 0x06:
		// Response
		switch msg[2] {
		case 0x00:
			return "OK", nil
		case 0x01:
			return "Error", nil
		default:
			return "", fmt.Errorf("invalid response value")
		}
	default:
		return "", fmt.Errorf("invalid response type")
	}

}
