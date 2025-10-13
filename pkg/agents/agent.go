package agents

type Agent interface {
	Execute(input string) (string, error)
}
