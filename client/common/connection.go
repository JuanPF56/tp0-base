package common

import (
	"encoding/binary"
	"fmt"
	"net"
)

// Connection Entity
type Connection struct {
	id   int
	conn net.Conn
}

// NewConnection: Initializes a new connection with the given server address and client id
func NewConnection(serverAddress string, id int) *Connection {
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
func (c *Connection) SendMessage(msg []byte) (int, error) {
	if c.conn == nil {
		return 0, fmt.Errorf("connection not initialized")
	}

	// Send the message size first
	size := make([]byte, 4)
	binary.BigEndian.PutUint32(size, uint32(len(msg)))
	sent := 0
	for sent < len(size) {
		n, err := c.conn.Write(size[sent:])
		if err != nil {
			return sent, err
		}
		sent += n
	}

	// Send the message
	sent = 0
	for sent < len(msg) {
		n, err := c.conn.Write(msg[sent:])
		if err != nil {
			return sent, err
		}
		sent += n
	}
	return sent, nil
}

// ReceiveMessage: Receives a message from the server avoiding short reads
func (c *Connection) ReceiveMessage() ([]byte, error) {
	if c.conn == nil {
		return nil, fmt.Errorf("connection not initialized")
	}

	// Read the message size first
	size := make([]byte, 4)
	read := 0
	for read < len(size) {
		n, err := c.conn.Read(size[read:])
		if err != nil {
			return nil, err
		}
		read += n
	}

	// Read the message
	msgSize := binary.BigEndian.Uint32(size)
	buf := make([]byte, msgSize)
	for read = 0; read < int(msgSize); {
		n, err := c.conn.Read(buf[read:])
		if err != nil {
			return nil, err
		}
		read += n
	}
	return buf, nil
}
