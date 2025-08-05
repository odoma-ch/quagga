# Quagga – Question answering over graphs
Quagga is a web appplication aimed at crowdsourcing a bechmark dataset for the task of Knowledge Graph Query Answering (KGQA) with a focus on Social Sciences and Humanities.

- Run the FastAPI instance for the crowdsourcing interface: `uvicorn main:app --reload` and access the main webpage: `http://127.0.0.1:8000/`
- Run a docker container with the MySQL DB to run it locally:
```
docker run --name my-mysql \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=mydb \
  -e MYSQL_USER=myuser \
  -e MYSQL_PASSWORD=mypassword \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  -d mysql:latest
```

- For exposing the local app for testing:
  - `brew install ngrok`
  - Authenticate online using ngrok account
  - `ngrok config add-authtoken <token-name>` which creates a ngrok.yaml file.
  - `ngrok http http://localhost:8002` to forward the FastAPI application running on 8002.


- How to add a new column to an existing table:
  ```
  import mysql.connector
  from dotenv import load_dotenv
  load_dotenv()

  conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
  )

  cursorr = conn.cursor()
  cursor.execute("ALTER TABLE kg_endpoints ADD COLUMN domains TEXT;")
  conn.close()
  ```