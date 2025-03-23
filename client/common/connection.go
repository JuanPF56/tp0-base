package common

import (
	"encoding/binary"
	"fmt"
	"net"
)

// Connection Entity
type Connection struct {
	id   string
	conn net.Conn
}

// NewConnection: Initializes a new connection with the given server address and client id
func NewConnection(serverAddress string, id string) *Connection {
	conn, err := net.Dial("tcp", serverAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			id,
			err,
		)
	}
	return &Connection{
		id:   id,
		conn: conn,
	}
}

// CloseConnection: Closes the connection if it is not already closed
func (c *Connection) CloseConnection() {
	// If the connection is not closed, close it
	if c.conn != nil {
		c.conn.Close()
		log.Infof("Closing server connection")
	}
}

// SendMessage: Sends a message to the server avoiding short writes
func (c *Connection) SendMessage(msg []byte) error {
	if c.conn == nil {
		return fmt.Errorf("Connection not initialized")
	}

	// Send the message size first
	size := make([]byte, 4)
	binary.BigEndian.PutUint32(size, uint32(len(msg)))
	_, err := c.conn.Write(size)
	if err != nil {
		return err
	}

	// Send the message
	sent := 0
	for sent < len(msg) {
		n, err := c.conn.Write(msg[sent:])
		if err != nil {
			return err
		}
		sent += n
	}
	return nil
}

// ReceiveMessage: Receives a message from the server avoiding short reads
func (c *Connection) ReceiveMessage() ([]byte, error) {
	if c.conn == nil {
		return nil, fmt.Errorf("Connection not initialized")
	}

	// Read the message size first
	size := make([]byte, 4)
	_, err := c.conn.Read(size)
	if err != nil {
		return nil, err
	}

	// Read the message
	msgSize := binary.BigEndian.Uint32(size)
	buf := make([]byte, msgSize)
	for read := 0; read < int(msgSize); {
		n, err := c.conn.Read(buf[read:])
		if err != nil {
			return nil, err
		}
		read += n
	}
	return buf, nil
}
