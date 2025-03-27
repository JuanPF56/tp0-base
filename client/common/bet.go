package common

type Bet struct {
	Name      string
	Surname   string
	DNI       int
	Birthdate string
	Number    int
}

type Winner struct {
	DNI    uint32
	Number uint32
}
