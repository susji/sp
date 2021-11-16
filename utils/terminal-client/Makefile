TC ?= venv/bin/python3 terminal-client.py

.PHONY: run
fetch: venv
	$(TC) fetch

.PHONY: submit
submit: venv
	$(TC) submit

venv:
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
