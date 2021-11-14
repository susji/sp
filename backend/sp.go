package main

import (
	"context"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
)

type server struct {
	laddr, endpoint string
}

func (s *server) fetch(r *http.Request, w http.ResponseWriter) {

}

func (s *server) submit(r *http.Request, w http.ResponseWriter) {

}

func (s *server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
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
		s.fetch(r, w)
		return
	default:
		log.Printf("bad request: %s (%s)", url, r.Method)
		w.WriteHeader(http.StatusBadRequest)
		return
	}
}

func main() {
	var logTimestamps bool
	s := &server{}

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
	flag.Parse()

	if logTimestamps {
		log.SetFlags(log.LstdFlags)
	} else {
		log.SetFlags(0)
	}

	log.Print("Listen address........ ", s.laddr)
	log.Print("Submission endpoint... ", s.endpoint)

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
