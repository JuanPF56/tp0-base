package common

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
)

// BetReader Entity
type BetReader struct {
	maxAmount int
	file      *os.File
	reader    *csv.Reader
}

// NewBetReader: Initializes a new bet reader with the given maximum amount and filename
func NewBetReader(maxAmount int, filename string) *BetReader {
	// Open the file
	file, err := os.Open(filename)
	if err != nil {
		log.Errorf("action: open_file | result: fail | error: %v", err)
		return nil
	}
	// Create the csv reader
	reader := csv.NewReader(file)
	// Return the bet reader
	return &BetReader{
		maxAmount: maxAmount,
		file:      file,
		reader:    reader,
	}
}

func (b *BetReader) GetNextBatch() ([]Bet, bool, error) {
	// If the file is closed, return an error
	if b.file == nil {
		return nil, false, fmt.Errorf("file is closed")
	}

	// Read the batch
	batch := make([]Bet, b.maxAmount)
	for i := 0; i < b.maxAmount; i++ {
		// Read the bet
		bet, err := b.readBet()
		if err != nil {
			// If there are no more bets, return the batch and flag EOF
			if err.Error() == "EOF" {
				return batch[:i], true, nil
			}
			return nil, false, err
		}
		batch[i] = bet
	}
	// Before returning the batch, check if there are no more bets
	eof := b.peekEOF()
	return batch, eof, nil
}

// readBet: Reads a bet from the file
func (b *BetReader) readBet() (Bet, error) {
	// Read next csv line
	var name, surname, birthdate string
	var dni, number int

	record, err := b.reader.Read()
	if err != nil {
		return Bet{}, err
	}

	// Parse the csv line
	name = record[0]
	surname = record[1]
	dni, err = strconv.Atoi(record[2])
	if err != nil {
		return Bet{}, err
	}
	birthdate = record[3]
	number, err = strconv.Atoi(record[4])
	if err != nil {
		return Bet{}, err
	}

	// Return the bet
	return Bet{
		Name:      name,
		Surname:   surname,
		DNI:       dni,
		Birthdate: birthdate,
		Number:    number,
	}, nil
}

// peekBet: Peeks if there are more bets to read
func (b *BetReader) peekEOF() bool {
	_, err := b.file.Seek(0, 1)
	return err != nil
}

// CloseFile: Closes the file if it is not already closed
func (b *BetReader) CloseFile() {
	// If the file is not closed, close it
	if b.file != nil {
		b.file.Close()
		log.Infof("Closing batch file")
	}
}
