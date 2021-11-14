GODEPS := $(shell find . -name '*.go')
GOOS ?= linux
GOARCH ?= amd64

sp: $(GODEPS) Makefile
	go vet ./...
	GOOS=$(GOOS) GOARCH=$(GOARCH) go build cmd/sp/sp.go

.PHONY: clean
clean:
	rm -f sp
