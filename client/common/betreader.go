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
	next_line []string
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
		bet, eof, err := b.readBet()
		if err != nil {
			return nil, false, err
		}
		batch[i] = bet
		if eof {
			return batch[:i+1], true, nil
		}
	}
	return batch, false, nil
}

// readBet: Reads a bet from the file
func (b *BetReader) readBet() (Bet, bool, error) {
	// Read next csv line
	var name, surname, birthdate string
	var dni, number int
	var record []string
	var err error
	eof := false

	// If there is a line in advance, use it
	if b.next_line == nil {
		record, err = b.reader.Read()
	} else {
		record = b.next_line
		b.next_line = nil
	}
	if err != nil {
		return Bet{}, false, err
	}

	// Parse the csv line
	name = record[0]
	surname = record[1]
	dni, err = strconv.Atoi(record[2])
	if err != nil {
		return Bet{}, false, err
	}
	birthdate = record[3]
	number, err = strconv.Atoi(record[4])
	if err != nil {
		return Bet{}, false, err
	}

	// Read the next line in advance to check if there are more bets
	temp_line, err := b.reader.Read()
	if err != nil {
		if err.Error() == "EOF" {
			eof = true
		} else {
			return Bet{}, false, err
		}
	} else {
		b.next_line = temp_line
	}

	// Return the bet
	return Bet{
		Name:      name,
		Surname:   surname,
		DNI:       dni,
		Birthdate: birthdate,
		Number:    number,
	}, eof, nil
}

// CloseFile: Closes the file if it is not already closed
func (b *BetReader) CloseFile() {
	// If the file is not closed, close it
	if b.file != nil {
		b.file.Close()
		log.Infof("Closing batch file")
	}
}
