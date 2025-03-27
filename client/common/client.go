package common

import (
	"fmt"
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
	ID             string
	ServerAddress  string
	LoopAmount     int
	LoopPeriod     time.Duration
	BatchMaxAmount int
	BatchFilename  string
}

// Client Entity
type Client struct {
	config     ClientConfig
	conn       Connection
	protocol   Protocol
	betReader  BetReader
	is_running bool
}

// NewClient: Initializes a new client with the given configuration
func NewClient(config ClientConfig) *Client {
	id, err := strconv.Atoi(config.ID)
	if err != nil {
		log.Errorf("action: id_conversion | result: fail | error: %v", err)
		return nil
	}
	client := &Client{
		config:     config,
		protocol:   Protocol{id: id},
		betReader:  *NewBetReader(config.BatchMaxAmount, config.BatchFilename),
		is_running: true,
	}
	conn := NewConnection(config.ServerAddress, id)
	client.conn = *conn
	return client
}

// StartClient: Starts the client logic
func (c *Client) StartClient() {
	// Set up signal handler to stop the client
	c.setUpSignalHandler()

	// Send the agency ID
	_, err := c.conn.SendMessage(c.protocol.CreateAgencyIDMessage())

	// Send the bet batches if there was no error
	if err == nil {
		err = c.sendBetBatches()
	}

	// Check winners if there was no error
	if err == nil {
		c.checkWinners()
	}

	// Close the connection and the file
	c.conn.CloseConnection()
	c.betReader.CloseFile()
}

// setUpSignalHandler: Sets up the signal handler to stop the client when a signal is received
func (c *Client) setUpSignalHandler() {
	// Signal handling to stop the client
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM, syscall.SIGINT)

	// Go routine to handle the signal
	go func() {
		<-sigChan
		c.is_running = false
		log.Infof("SIGTERM received, stopping client %v", c.config.ID)
		c.conn.CloseConnection()
		c.betReader.CloseFile()
	}()
}

// checkWinners: Await server response for winners
func (c *Client) checkWinners() {
	// Wait for the response
	response, err := c.conn.ReceiveMessage()
	if err != nil {
		log.Errorf("action: consultar_ganadores | result: fail | error: %v", err)
		return
	}

	// Parse the response
	winners, err := c.protocol.ParseWinners(response)
	if err != nil {
		log.Errorf("action: consultar_ganadores | result: fail | error: %v", err)
		return
	}

	// Log the winners
	log.Infof("action: consultar_ganadores | result: success | cant_ganadores: %v", len(winners))
}

// sendBetBatches: Sends the bet batches to the server
func (c *Client) sendBetBatches() error {
	last_batch := false
	current_batch := 0
	// Loop until the client is stopped, there are no more batches or an error occurs
	for c.is_running && !last_batch {
		var err error
		last_batch, err = c.sendNextBatch(current_batch)
		// If there was an error sending the batch, stop sending batches
		if err != nil {
			return err
		}
		if c.is_running {
			// If the response was unsuccessful, stop sending batches
			if !c.handleBatchResponse(current_batch) {
				return fmt.Errorf("batch %v was unsuccessful", current_batch)
			}
		}
		current_batch++
	}
	return nil
}

// sendNextBatch: Sends the next batch of bets to the server
func (c *Client) sendNextBatch(current_batch int) (bool, error) {
	// Get the next batch of bets
	batch, is_last_batch, err := c.betReader.GetNextBatch()
	if err != nil {
		log.Errorf("action: obtener_apuestas | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return false, err
	}
	// Send the batch to the server
	_, err = c.conn.SendMessage(c.protocol.CreateBetBatchMessage(batch, is_last_batch))
	if err != nil {
		log.Errorf("action: apuestas_enviadas | result: fail | client_id: %v | batch_number: %v | error: %v", c.config.ID, current_batch, err)
		return false, err
	}
	return is_last_batch, nil
}

// handleBatchResponse: Handles the response from the server after sending a batch of bets
func (c *Client) handleBatchResponse(current_batch int) bool {
	// Wait for the response
	response, err := c.conn.ReceiveMessage()
	if err != nil {
		log.Errorf("action: apuestas_enviadas | result: fail | client_id: %v | batch_number: %v | error: %v", c.config.ID, current_batch, err)
		return false
	}

	// Parse the response
	err = c.protocol.ParseResponse(response)
	if err != nil {
		log.Errorf("action: apuestas_enviadas | result: fail | client_id: %v | batch_number: %v | error: %v", c.config.ID, current_batch, err)
		return false
	}

	// Log the result if successful
	log.Infof("action: apuestas_enviadas | result: success | client_id: %v | batch_number: %v", c.config.ID, current_batch)

	return true
}
