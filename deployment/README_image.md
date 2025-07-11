## For setting up the image:
- Get the token from logging into the UI, click on the top right corner and go to User Profile and copy the CLI secret
- docker login registry.pass.psnc.pl
- Input your username and password
- `docker build --platform linux/amd64 . -t registry.paas.psnc.pl/graphia/kgqa-crowdsourcing-app:v0.3` (remember to put the platform flag otherwise it will build for your local machine architecture)
- `docker push registry.paas.psnc.pl/graphia/kgqa-crowdsourcing-app:v0.3` (push the image on the container registry)
- For access related issues, contact PSNC.


## For setting up the Route:
- Under Networking, go to Routes and click on Create Route.
- Add name of the service you want to attach to and also the port you want to select
- Set the security to be "Secure Route" and set the TLS termination to be "Edge" and Insecure traffic to be "Redirect"
- for the route to be public and accessible anywhere: haproxy.router.openshift.io/ip_whitelist: 0.0.0.0/0
