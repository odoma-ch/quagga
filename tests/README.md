## How to run the locust test:

- Go to Safari, and then go to Inspect Element, go to Storage and then cookies.
- Copy the value of the `session` key and make it into an environment variable: `SESSION_KEY`.
- The webserver/app must be running at `localhost:8004` for the below command to run.
- Run the tests using the following command after running the web server: `locust -f tests/locustfile.py --host=http://localhost:8004 --users 100 --spawn-rate 10 --run-time 5m --headless`
