package main

import (
	"context"
	"flag"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"

	"github.com/susji/sp/storage"
)

var (
	version   = "v0.dev"
	buildtime = "<no time>"
)

const (
	BYTES_ID      = 4
	MAX_ENTRIES   = 10_000
	MAXLEN_SUBMIT = 1024 * 5
)

type server struct {
	laddr, endpoint string
	wildcardCors    bool

	storage *storage.Storage
}

func (s *server) fetch(r *http.Request, w http.ResponseWriter, id string) {
	e := s.storage.Fetch(id)
	if e == nil {
		log.Print("fetch: cannot find with id: ", id)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	if _, err := w.Write(e); err != nil {
		log.Print("fetch: response write failed: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	log.Print("fetch: ", id)
}

func (s *server) submit(r *http.Request, w http.ResponseWriter) {
	mr := http.MaxBytesReader(w, r.Body, MAXLEN_SUBMIT)
	defer mr.Close()
	body, err := io.ReadAll(mr)
	if err != nil {
		log.Print("submit: body read failed: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	id, err := s.storage.Insert(body)
	if err != nil {
		log.Print("submit: storage insertion failed: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	if _, err := w.Write([]byte(id)); err != nil {
		log.Print("submit: id write failed: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	log.Printf("submit: got %d bytes with id %s", len(body), id)
}

func (s *server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if s.wildcardCors {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
		w.Header().Set(
			"Access-Control-Allow-Headers",
			"Accept, Content-Type, Content-Length")
	}
	if r.Method == "OPTIONS" {
		return
	}
	if len(r.URL.Path) == 0 {
		log.Print("empty request")
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	url := r.URL.Path[1:]
	switch {
	case url == s.endpoint && r.Method == "POST":
		s.submit(r, w)
		return
	case r.Method == "GET":
		s.fetch(r, w, url)
		return
	default:
		log.Printf("bad request: %s (%s)", url, r.Method)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
}

func main() {
	var logTimestamps bool
	s := &server{storage: storage.New(MAX_ENTRIES, MAXLEN_SUBMIT, BYTES_ID)}

	flag.StringVar(&s.laddr, "listen", "localhost:19680", "HTTP listen address")
	flag.BoolVar(
		&logTimestamps,
		"log-timestamps",
		false,
		"Whether to include timestamps in log messages")
	flag.StringVar(
		&s.endpoint,
		"endpoint",
		"submit",
		"Endpoint for posting new pastes")
	flag.BoolVar(
		&s.wildcardCors,
		"wildcard-cors",
		false,
		"Essentially 'Access-Control-Allow-Origin=*'")
	flag.Parse()

	if logTimestamps {
		log.SetFlags(log.LstdFlags)
	} else {
		log.SetFlags(0)
	}

	log.Printf("sp version: %s built at %s", version, buildtime)
	log.Print("Listen address........ ", s.laddr)
	log.Print("Submission endpoint... ", s.endpoint)
	log.Print("Wildcard CORS......... ", s.wildcardCors)

	ctx, cancel := context.WithCancel(context.Background())
	srv := http.Server{Addr: s.laddr, Handler: s}
	sigint := make(chan os.Signal, 1)
	signal.Notify(sigint, os.Interrupt)
	go func() {
		<-sigint
		log.Print("SIGINT received")
		cancel()
		srv.Shutdown(ctx)
	}()
	if err := srv.ListenAndServe(); err != nil {
		log.Print(err)
	}
}
