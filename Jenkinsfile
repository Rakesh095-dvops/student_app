pipeline {
    agent any

    environment {
        EC2_IP_STG = '13.233.151.198'
        EC2_IP_PRD = '13.204.46.90'
        EC2_USERNAME='ubuntu'
        SSH_CREDS = 'rik-ssh-creds' // Jenkins credentials ID for SSH access 
        MONGO_URI = 'mongodb+srv://mngadmin:oA3jBP6293OA6lGx@cluster0.i0pov.mongodb.net/?retryWrites=true&w=majority'
        DB_NAME = 'student'
        STG_COLLECTION_NAME = 'test_students'
        STAGING_APP_URL = "http://${EC2_IP_STG}:5000"

        PRD_COLLECTION_NAME = 'students'
        PRD_APP_URL = "http://${EC2_IP_PRD}:5000"
        GIT_REPO_URL='https://github.com/Rakesh095-dvops/student_app.git'
        GIT_BRANCH='main'
        
        DOCKER_REGISTRY = 'docker.io/crashrik' // Corrected: Just the registry server, e.g., 'docker.io' for Docker Hub
        APP_NAME = 'student-app'
        DOCKER_CREDENTIALS_ID = 'docker-rakesh'
        // Construct the full Docker image name
        DOCKER_IMAGE_FULL_NAME = "${DOCKER_REGISTRY}/${APP_NAME}"
        EMAIL_RECIPIENTS="crashrik89@gmail.com"
        
        }
    stages {
        stage('Check Docker') {
            steps {
                sh 'docker --version'
                sh 'docker-compose --version'
            }
        }
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out Git repository: ${env.GIT_REPO_URL}, branch: ${env.GIT_BRANCH}"
                    // Explicitly capture the Git commit hash
                    def gitCommit = checkout(scm: [
                        $class: 'GitSCM',
                        branches: [[name: env.GIT_BRANCH]],
                        userRemoteConfigs: [[url: env.GIT_REPO_URL]]
                    ]).GIT_COMMIT
                    env.GIT_COMMIT = gitCommit  // Set it in the environment
                }
            }
        }
        stage('Unit Tests') {
            steps {
                sh '''#!/bin/bash
                # Create a virtual environment
                python3 -m venv .venv
                
                # Activate the virtual environment
                source .venv/bin/activate
                
                # Install dependencies into the virtual environment
                pip install -r requirements.txt

                 # Create .env file for unit tests
                echo "MONGO_URI=${MONGO_URI}" > .env
                echo "DB_NAME=${DB_NAME}" >> .env
                echo "COLLECTION_NAME=${STG_COLLECTION_NAME}" >> .env # Use staging collection for unit tests
                
                # Run tests using the Python from the virtual environment
                pytest --maxfail=1 --disable-warnings --tb=short
                #pytest test_app.py -vvs 
                
                # Deactivate (optional, as the shell session will end)
                deactivate
                '''
            }
        }
        stage('Build & Push Docker Image') {
            steps {
                script {
                    // Safely handle GIT_COMMIT (null check)
                    def commitHash = env.GIT_COMMIT ? env.GIT_COMMIT.substring(0, 7) : "unknown"
                    def imageTag = "${env.BUILD_NUMBER}-${commitHash}"
                    env.IMAGE_TAG = imageTag
                    echo "Building Docker image with tag: ${imageTag}"

                    withCredentials([usernamePassword(
                        credentialsId: env.DOCKER_CREDENTIALS_ID, 
                        usernameVariable: 'DOCKER_USER', 
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                            docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${env.DOCKER_REGISTRY}
                            docker build -t ${env.DOCKER_IMAGE_FULL_NAME}:${env.IMAGE_TAG} -f Dockerfile .
                            docker push ${env.DOCKER_IMAGE_FULL_NAME}:${env.IMAGE_TAG}
                        """
                    }
                }
            }
        }
        stage('Deploy to Staging') {
            steps {
                // Step 1: Create .env file locally for scp
                sh '''
                echo "MONGO_URI=${MONGO_URI}" > .env
                echo "DB_NAME=${DB_NAME}" >> .env
                echo "COLLECTION_NAME=${STG_COLLECTION_NAME}" >> .env
                echo "IMAGE_NAME=${DOCKER_IMAGE_FULL_NAME}" >> .env
                echo "IMAGE_TAG=${IMAGE_TAG}" >> .env
                '''
        
                sshagent(credentials: ["${env.SSH_CREDS}"]) {
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        sh """
                        # Ensure the target directory exists and is clean before copying
                        ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP_STG} "mkdir -p /home/ubuntu && rm -rf /home/ubuntu/*"
        
                        # Copy all necessary files (including .env, docker-compose files) to the EC2 instance
                        scp -o StrictHostKeyChecking=no -r .env docker-compose.yml docker-compose.staging.yml ${env.EC2_USERNAME}@${env.EC2_IP_STG}:/home/ubuntu/
        
                        # Use a single quoted here-document to prevent local variable expansion
                        ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP_STG} /bin/bash -s << 'EOF'
                        cd /home/ubuntu
        
                        # Step 2: Log in to Docker Registry on the remote EC2 instance
                        echo "Logging in to Docker registry..."
                        docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${DOCKER_REGISTRY}
        
                        # Step 3: Pull the latest Docker image on the remote EC2 instance
                        echo "Pulling Docker image: ${DOCKER_IMAGE_FULL_NAME}:${IMAGE_TAG}"
                        docker pull ${DOCKER_IMAGE_FULL_NAME}:${IMAGE_TAG}
        
                        # Step 4: Docker compose commands
                        echo "Running docker compose up..."
                        echo "${DOCKER_IMAGE_FULL_NAME} : ${IMAGE_TAG}"
                        sudo docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file ./.env up -d --remove-orphans
                        
                        echo "Container status:"
                        sudo docker-compose ps
                        sudo docker-compose logs app
EOF
                        """
                    }
                }
            }
        }
        stage('Staging Tests (Integration)') {
                steps {
                    script {
                        echo "Running integration tests on staging environment at ${env.STAGING_APP_URL}..."
                        sh "curl -f ${env.STAGING_APP_URL}/health || exit 1"
                    }
                }
            }
        stage('Deploy to Production') {
                steps {
                    // Step 1: Create .env file locally for scp
                    sh '''
                    echo "MONGO_URI=${MONGO_URI}" > .env
                    echo "DB_NAME=${DB_NAME}" >> .env
                    echo "COLLECTION_NAME=${PRD_COLLECTION_NAME}" >> .env
                    echo "IMAGE_NAME=${DOCKER_IMAGE_FULL_NAME}" >> .env
                    echo "IMAGE_TAG=${IMAGE_TAG}" >> .env
                    '''
            
                    sshagent(credentials: ["${env.SSH_CREDS}"]) {
                        withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                            sh """
                            # Ensure the target directory exists and is clean before copying
                            ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP_PRD} "mkdir -p /home/ubuntu && rm -rf /home/ubuntu/*"
            
                            # Copy all necessary files (including .env, docker-compose files) to the EC2 instance
                            scp -o StrictHostKeyChecking=no -r .env docker-compose.yml docker-compose.prod.yml ${env.EC2_USERNAME}@${env.EC2_IP_PRD}:/home/ubuntu/
            
                            # Use a single quoted here-document to prevent local variable expansion
                            ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP_PRD} /bin/bash -s << 'EOF'
                            cd /home/ubuntu
            
                            # Step 2: Log in to Docker Registry on the remote EC2 instance
                            echo "Logging in to Docker registry..."
                            docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${DOCKER_REGISTRY}
            
                            # Step 3: Pull the latest Docker image on the remote EC2 instance
                            echo "Pulling Docker image: ${DOCKER_IMAGE_FULL_NAME}:${IMAGE_TAG}"
                            docker pull ${DOCKER_IMAGE_FULL_NAME}:${IMAGE_TAG}
            
                            # Step 4: Docker compose commands
                            echo "Running docker compose up..."
                            echo "${DOCKER_IMAGE_FULL_NAME} : ${IMAGE_TAG}"
                            sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file ./.env up -d --remove-orphans
                            
                            echo "Container status:"
                            sudo docker-compose ps
                            sudo docker-compose logs app                                
EOF
                            """
                        }
                    }
                }
            }
        stage('Production Tests (Integration)') {
                steps {
                    script {
                        echo "Running integration tests on production environment at ${env.PRD_APP_URL}..."
                        sh "curl -f ${env.PRD_APP_URL}/health || exit 1"
                    }
                }
            }
        }
    post {
        always {
            cleanWs()
        }
        success {
            script {
                mail(
                    to: env.EMAIL_RECIPIENTS,
                    subject: "[Jenkins] SUCCESS: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: """
                        Hello Team,
                        The pipeline for ${env.JOB_NAME} (Build #${env.BUILD_NUMBER}) completed successfully.
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${env.GIT_COMMIT}
                        Image Tag: ${env.IMAGE_TAG}
                        View build details: ${env.BUILD_URL}
                        Regards,
                        Jenkins CI/CD
                    """.stripIndent()
                )
            }
        }
        failure {
            script {
                mail(
                    to: env.EMAIL_RECIPIENTS,
                    subject: "[Jenkins] FAILED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: """
                        Hello Team,
                        The pipeline for ${env.JOB_NAME} (Build #${env.BUILD_NUMBER}) FAILED!
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${env.GIT_COMMIT}
                        Please investigate the build logs: ${env.BUILD_URL}
                        Regards,
                        Jenkins CI/CD
                    """.stripIndent()
                )
            }
        }
        aborted {
            script {
                mail(
                    to: env.EMAIL_RECIPIENTS,
                    subject: "[Jenkins] ABORTED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                    body: """
                        Hello Team,
                        The pipeline for ${env.JOB_NAME} (Build #${env.BUILD_NUMBER}) was ABORTED.
                        View build details: ${env.BUILD_URL}
                        Regards,
                        Jenkins CI/CD
                    """.stripIndent()
                )
            }
        }
    }
}