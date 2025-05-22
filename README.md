# Student Management System (Flask + Pytest + Jenkins + Docker)

## 📌 Features
- Add, view, fetch, and delete students
- REST API with Flask
- Tested with pytest
- Dockerized
- CI/CD ready with Jenkins

## 🚀 Run Locally

-Create ```.env``` file and filled in details.

```
MONGO_URI={mongoDB Connection String}
DB_NAME= {database name }
COLLECTION_NAME={collection details}
```

```bash
pip install -r requirements.txt
python app.py
```

## 🧪 Run Tests
```bash
pytest test_app.py -vvs
```

## 🐳 Docker

```bash
docker build -t student-api .
docker run -p 5000:5000 student-api
```
## 🐳 Docker-Compose 
- ```docker-compose.yml```- (Base/Common) for docker compose for development used with earlier ```.env```
- ```docker-compose.staging.yml``` - For Staging 
- ```docker-compose.prod.yml``` - For Production 

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --remove-orphans
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans
docker compose ps 
```

## 🛠️ Jenkins Pipeline
This project contains a `Jenkinsfile` to automate:
- Code clone
- Dependency install
- Test execution
- App deployment
