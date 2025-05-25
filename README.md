# Student Management System (Flask + Pytest + Jenkins + Docker)

## 📌 Features
- Add, view, fetch, and delete students
- REST API with Flask
- Tested with pytest
- Dockerize using docker-compose 
- CI/CD ready with Jenkins and git Action 

## 🚀 Run Locally

1. **Create a `.env` file** and fill in the following details:
    ```
    MONGO_URI={mongoDB Connection String}
    DB_NAME={database name}
    COLLECTION_NAME={collection name}
    ```

2. **Install dependencies and run the app:**
    ```bash
    pip install -r requirements.txt
    python app.py
    ```

## 🧪 Run Tests

- Run all unit tests using pytest:
    ```bash
    pytest test_app.py -vvs
    ```

## 🐳 Docker

- Build and run the Docker image:
    ```bash
    docker build -t student-api .
    docker run -p 5000:5000 student-api
    ```

## 🐳 Docker Compose

- **docker-compose.yml**: Base/common for development (used with `.env`)
- **docker-compose.staging.yml**: For staging environment
- **docker-compose.prod.yml**: For production environment

- Example commands:
    ```bash
    docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --remove-orphans
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans
    docker compose ps
    ```

## 🛠️ Jenkins Pipeline

This project contains a `Jenkinsfile` to automate the following stages:
- Check Docker
- Checkout Code
- Unit Tests (with pytest)
- Build & Push Docker Image
- Deploy to Staging
- Staging Tests (Integration)
- Deploy to Production
- Production Tests (Integration)
- Post Actions:
    - Always: Clean workspace
    - On success/failure/aborted: Send email with build details

> **For detailed CI/CD steps, refer to the [Jenkins Readme](https://github.com/Rakesh095-dvops/student_app/blob/main/Jenkins/README_J.MD).**

##  🛠️ GitHub Workflow Action 
This project contains a `.github\workflows\ci-cd.yml` to automate the github action pass through following stages 
- install-dependencies
- run-tests
- build docker image
- deploy-staging
- deploy-production
> **For detailed CI/CD steps, refer to the [Git Action Readme](https://github.com/Rakesh095-dvops/student_app/blob/main/gitaction/README.MD).**
---
## 💻 EC2 AWS Setup 
```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create symlink for 'docker compose' command if not already there (v2 usually auto-installs it)
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose # For compatibility

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker  # Refresh group permissions
```