# sp

`sp` is a minimalistic encrypted pastebin-clone. Presently it's mainly
a proof-of-concept, so I advise against running it in production. In
fact, it is better to assume that it's **unsafe** for use. In any case,
you probably want to run it behind some TLS-terminating reverse proxy,
so nginx stuff is included in the example deployment file.

## usage

	$ sp -h

## deploying

In this example case, your site's address would be
`https://a.example.com`. The deployment script will automatically
attempt to get you an Let's Encrypt certificate. Your browser
interface would be at `https://a.example.com/sp` and the backend's
submission endpoint would be `https://a.example.com/submit`.

	$ make
	$ python3 -m venv ~/venv-pyinfra
	$ ~/venv-pyinfra/bin/pip install -r deploy/requirements.txt
	$ source ~/venv-pyinfra/bin/activate
	$ cd deploy
	$ pyinfra \
		--data SP_DOMAIN=a.example.com \
		--data FRONTEND_PATH=sp \
		--data BACKEND_ENDPOINT_SUBMIT=submit \
		a.example.com deploy.py
