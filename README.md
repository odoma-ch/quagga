# kgqa-crowdsourcing-app
KGQA crowdsourcing app for natural language and SPARQL queries

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

