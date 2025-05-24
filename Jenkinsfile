pipeline {
    agent any

    environment {
        EC2_IP = '13.233.151.198'
        EC2_USERNAME='ubuntu'
        SSH_CREDS = 'rik-ssh-creds'
        MONGO_URI = 'mongodb+srv://mngadmin:oA3jBP6293OA6lGx@cluster0.i0pov.mongodb.net/?retryWrites=true&w=majority'
        DB_NAME = 'student'
        STG_COLLECTION_NAME = 'test_students'
        PRD_COLLECTION_NAME = 'students'
        GIT_REPO_URL='https://github.com/Rakesh095-dvops/student_app.git'
        GIT_BRANCH='main'
        
        DOCKER_REGISTRY = 'docker.io/crashrik' // Corrected: Just the registry server, e.g., 'docker.io' for Docker Hub
        APP_NAME = 'student-app'
        DOCKER_CREDENTIALS_ID = 'docker-rakesh'
        
        // This should be the full image name including org/username
        // It's constructed here to ensure it's available throughout the pipeline
        DOCKER_IMAGE_FULL_NAME = "${DOCKER_REGISTRY}/${APP_NAME}"
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
                sh """
                echo "MONGO_URI=${env.MONGO_URI}" > .env
                echo "DB_NAME=${env.DB_NAME}" >> .env
                echo "COLLECTION_NAME=${env.STG_COLLECTION_NAME}" >> .env
                """

                sshagent(credentials: ["${env.SSH_CREDS}"]) {
                    // Fix: Use env.DOCKER_CREDENTIALS_ID here, as it's defined in environment block
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        sh """
                        # Ensure the target directory exists and is clean before copying
                        ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} "mkdir -p /home/ubuntu && rm -rf /home/ubuntu/*"

                        # Copy all necessary files (including .env, docker-compose files) to the EC2 instance
                        scp -o StrictHostKeyChecking=no -r .env docker-compose.yml docker-compose.staging.yml ${env.EC2_USERNAME}@${env.EC2_IP}:/home/ubuntu/

                        ssh -o StrictHostKeyChecking=no ${env.EC2_USERNAME}@${env.EC2_IP} << 'EOF'
                        cd /home/ubuntu

                        # Step 2: Log in to Docker Registry on the remote EC2 instance
                        echo "Logging in to Docker registry..."
                        # Use the variables injected by withCredentials. DOCKER_REGISTRY should be the server URL.
                        docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${env.DOCKER_REGISTRY}

                        # Step 3: Pull the latest Docker image on the remote EC2 instance
                        echo "Pulling Docker image: ${env.DOCKER_IMAGE_FULL_NAME}:${env.IMAGE_TAG}"
                        docker pull ${env.DOCKER_IMAGE_FULL_NAME}:${env.IMAGE_TAG}

                        # Step 4: Docker compose commands
                        echo "Running docker compose up..."
                        docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file ./.env up -d --remove-orphans
                        
                        echo "Displaying application logs..."
                        docker compose logs app
                        EOF
                        """
                    }
                }
            }
        }
    }
}