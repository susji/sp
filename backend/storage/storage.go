package storage

import (
	crand "crypto/rand"
	"encoding/base64"
	"errors"
)

var (
	ErrorStorageFull       = errors.New("storage is full")
	ErrorInsertionTooLarge = errors.New("submission is too large")
)

type Entries map[string][]byte

type Storage struct {
	MaxEntries, MaxSize, BytesId int

	Entries Entries
}

func New(maxentries, maxsz, bytesid int) *Storage {
	return &Storage{
		MaxEntries: maxentries,
		MaxSize:    maxsz,
		BytesId:    bytesid,
		Entries:    Entries{},
	}
}

func (s *Storage) Insert(data []byte) (string, error) {
	if s.MaxEntries > 0 && len(s.Entries) > s.MaxEntries {
		return "", ErrorStorageFull
	}
	// MaxSize has to be something -- we will *NOT* allow
	// unlimited.
	if len(data) > s.MaxSize {
		return "", ErrorInsertionTooLarge
	}
	idraw := make([]byte, s.BytesId)
	if _, err := crand.Read(idraw); err != nil {
		return "", err
	}
	id := base64.URLEncoding.EncodeToString(idraw)
	s.Entries[id] = data
	return id, nil
}

func (s *Storage) Fetch(id string) []byte {
	entry, ok := s.Entries[id]
	if !ok {
		return nil
	}
	return entry
}
