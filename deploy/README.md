# deploy

	$ make && scp backend/sp frontend/* deploy/* ${server}:
	$ ssh -t ${server} "export YOUR_DOMAIN=yourdomain; sudo --preserve-env=YOUR_DOMAIN /bin/sh -x x.sh"

