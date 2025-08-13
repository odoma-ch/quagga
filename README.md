# Quagga – Question answering over graphs
Quagga is a web appplication aimed at crowdsourcing a bechmark dataset for the task of Knowledge Graph Query Answering (KGQA) with a focus on Social Sciences and Humanities.


## Run it locally
- Make sure you have ngrok installed and install the requirements in the project using: `pip install -r requirements.txt`
- Also make sure you have a copy of the `.env` file which is needed for it to run
- Run the FastAPI instance for the crowdsourcing interface: `uvicorn main:app --host 0.0.0.0 --port 8004` and access the main webpage: `http://127.0.0.1:8004/`
- For exposing the local app for testing (needed for authentication):
  - `brew install ngrok`
  - Authenticate online using ngrok account
  - `ngrok config add-authtoken <token-name>` which creates a ngrok.yaml file.
  - `ngrok http http://localhost:8004` to forward the FastAPI application running on 8004.
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

## Updating the database
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

  cursor = conn.cursor()
  cursor.execute("ALTER TABLE kg_endpoints ADD COLUMN domains TEXT;")
  conn.commit()
  conn.close()
  ```
- To delete the column: `cursor.execute("ALTER TABLE kg_endpoints DROP COLUMN domains;")`
- Update the value for kg endpoints domain: 
  ```
  cursor.execute("UPDATE kg_endpoints SET domains = 'art' WHERE name = 'Swiss Art Research - BSO';")
  ```
