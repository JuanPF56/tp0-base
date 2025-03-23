package common

import (
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity
type Client struct {
	config     ClientConfig
	conn       Connection
	protocol   Protocol
	is_running bool
}

// NewClient: Initializes a new client with the given configuration
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:     config,
		protocol:   Protocol{},
		is_running: true,
	}
	conn := NewConnection(config.ServerAddress, config.ID)
	client.conn = *conn
	return client
}

// StartClient: Sends bet message to the server based on env variables and waits for a response
func (c *Client) StartClient() {
	// Get environment variables (these values will be replaced by reading from a file in the future)
	name := os.Getenv("NOMBRE")
	surname := os.Getenv("APELLIDO")
	dniStr := os.Getenv("DOCUMENTO")
	dni, err := strconv.Atoi(dniStr)
	if err != nil {
		log.Errorf("action: convert_dni | result: fail | error: %v", err)
		return
	}
	birthdate := os.Getenv("NACIMIENTO")
	numberStr := os.Getenv("NUMERO")
	number, err := strconv.Atoi(numberStr)
	if err != nil {
		log.Errorf("action: convert_number | result: fail | error: %v", err)
		return
	}

	// Signal handling to stop the client
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM, syscall.SIGINT)

	// Go routine to handle the signal
	go func() {
		<-sigChan
		c.is_running = false
		log.Infof("SIGTERM received, stopping client %v", c.config.ID)
		c.conn.CloseConnection()
	}()

	err := c.conn.SendMessage(protocol.CreateBetMessage(name, surname, dni, birthdate, number))
	if err != nil {
		log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	response, err := c.conn.ReceiveMessage()
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	parsedResponse, err := c.protocol.ParseResponse(response)
	if err != nil {
		log.Errorf("action: parse_response | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	if parsedResponse == "OK" {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			dni,
			number,
		)
	} else {
		log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v",
			dni,
			number,
		)
	}

	c.conn.CloseConnection()
}
