.PHONY: run
run: venv
	venv/bin/python3 terminal-client.py

venv:
	python3 -m venv venv
	venv/bin/pip3 install -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
