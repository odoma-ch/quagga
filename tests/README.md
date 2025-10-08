## How to run the locust test:

- Go to Safari, and then go to Inspect Element, go to Storage and then cookies.
- Copy the value of the `session` key and make it into an environment variable: `SESSION_KEY`.
- The webserver/app must be running at `localhost:8004` for the below command to run.
- Run the tests using the following command after running the web server: `locust -f tests/locustfile.py --host=http://localhost:8004 --users 100 --spawn-rate 10 --run-time 5m --headless`


## Extract of the result of the tests:

<img width="1187" height="192" alt="Screenshot 2025-10-08 at 15 28 23" src="https://github.com/user-attachments/assets/4f702452-0bd1-40fe-9a5f-22745af9cf46" />
