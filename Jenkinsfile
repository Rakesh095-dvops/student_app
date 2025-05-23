// Jenkinsfile
pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io/crashrik'
        APP_NAME = 'student-app'
        DOCKER_CREDENTIALS_ID = 'your-docker-hub-credentials-id'
        EC2_STAGING_SSH_CREDENTIALS_ID = 'ec2-staging-ssh-key'
        EC2_PROD_SSH_CREDENTIALS_ID = 'ec2-prod-ssh-key'
        EC2_STAGING_HOST = 'ubuntu@ec2-XXX-XXX-XXX-XXX.compute-1.amazonaws.com'
        EC2_PROD_HOST = 'ubuntu@ec2-YYY-YYY-YYY-YYY.compute-1.amazonaws.com'
        AWS_REGION = 'ap-south-1'
        ECR_REPO = "${DOCKER_REGISTRY}/${APP_NAME}"

        // Email Notification Variables
        SUCCESS_RECIPIENTS = 'crashrik89@gmail.com'
        FAILURE_RECIPIENTS = 'crashrik89@gmail.com'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Rakesh095-dvops/student_app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def imageTag = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.substring(0, 7)}"
                    env.IMAGE_TAG = imageTag
                    echo "Building Docker image with tag: ${imageTag}"

                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${DOCKER_REGISTRY}"
                        sh "docker build -t ${ECR_REPO}:${imageTag} -f Dockerfile ."
                        sh "docker push ${ECR_REPO}:${imageTag}"
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            steps {
                withCredentials([
                    sshUserPrivateKey(credentialsId: env.EC2_STAGING_SSH_CREDENTIALS_ID, keyFileVariable: 'SSH_KEY'),
                    usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')
                ]) {
                    sh """
                        scp -i ${SSH_KEY} docker-compose.yml ${env.EC2_STAGING_HOST}:/home/ubuntu/your-app/
                        scp -i ${SSH_KEY} docker-compose.staging.yml ${env.EC2_STAGING_HOST}:/home/ubuntu/your-app/
                        scp -i ${SSH_KEY} .env.staging ${env.EC2_STAGING_HOST}:/home/ubuntu/your-app/.env

                        ssh -i ${SSH_KEY} ${env.EC2_STAGING_HOST} <<EOF
                            cd /home/ubuntu/your-app/
                            export IMAGE_TAG=${env.IMAGE_TAG}
                            export DOCKER_USER=${DOCKER_USER}
                            export DOCKER_PASS=${DOCKER_PASS}
                            docker login -u \${DOCKER_USER} -p \${DOCKER_PASS} ${DOCKER_REGISTRY}
                            docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file ./.env up -d --remove-orphans
                            docker compose logs app
                        EOF
                    """
                }
            }
        }

        stage('Staging Tests (Integration)') {
            steps {
                echo "Running integration tests on staging environment..."
                sh "curl -f http://your-staging-app-url:5000/health || exit 1"
            }
        }

        stage('Run Unit Tests (Staging MongoDB)') {
            steps {
                withCredentials([
                    string(credentialsId: 'MONGO_URI_STAGING_SECRET_ID', variable: 'MONGO_URI_STAGING')
                ]) {
                    sh """
                        docker run --rm \
                            -e MONGO_URI="${MONGO_URI_STAGING}" \
                            -e DB_NAME="student" \
                            -e COLLECTION_NAME="test_students" \
                            ${ECR_REPO}:${env.IMAGE_TAG} \
                            /usr/local/bin/python -m pytest /app/test_app.py -vvs
                    """
                }
            }
        }

        stage('Manual Approval') {
            steps {
                input message: 'App deployed to Staging. Proceed to Production?'
            }
        }

        stage('Deploy to Production') {
            steps {
                withCredentials([
                    sshUserPrivateKey(credentialsId: env.EC2_PROD_SSH_CREDENTIALS_ID, keyFileVariable: 'SSH_KEY'),
                    usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS'),
                    string(credentialsId: 'MONGO_URI_PROD_SECRET_ID', variable: 'MONGO_URI_PROD')
                ]) {
                    sh """
                        scp -i ${SSH_KEY} docker-compose.yml ${env.EC2_PROD_HOST}:/home/ubuntu/your-app/
                        scp -i ${SSH_KEY} docker-compose.prod.yml ${env.EC2_PROD_HOST}:/home/ubuntu/your-app/

                        ssh -i ${SSH_KEY} ${env.EC2_PROD_HOST} <<EOF
                            cd /home/ubuntu/your-app/
                            export IMAGE_TAG=${env.IMAGE_TAG}
                            export MONGO_URI="${MONGO_URI_PROD}"
                            export DB_NAME="student"
                            export COLLECTION_NAME="students"
                            docker login -u \${DOCKER_USER} -p \${DOCKER_PASS} ${DOCKER_REGISTRY}
                            docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --remove-orphans
                            docker compose logs app
                        EOF
                    """
                }
            }
        }

        stage('Production Tests (Smoke)') {
            steps {
                echo "Running smoke tests on production environment..."
                sh "curl -f http://your-production-app-url:5000/health || exit 1"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline finished successfully. Sending success email...'
            mail(
                to: "${env.SUCCESS_RECIPIENTS}",
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
                """
            )
        }
        failure {
            echo 'Pipeline failed. Sending failure email...'
            mail(
                to: "${env.FAILURE_RECIPIENTS}",
                subject: "[Jenkins] FAILED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                    Hello Team,

                    The pipeline for ${env.JOB_NAME} (Build #${env.BUILD_NUMBER}) FAILED!

                    Branch: ${env.BRANCH_NAME}
                    Commit: ${env.GIT_COMMIT}

                    Please investigate the build logs for details: ${env.BUILD_URL}

                    Regards,
                    Jenkins CI/CD
                """
            )
        }
        aborted {
            echo 'Pipeline aborted. Sending email...'
            mail(
                to: "${env.FAILURE_RECIPIENTS}",
                subject: "[Jenkins] ABORTED: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
                body: """
                    Hello Team,

                    The pipeline for ${env.JOB_NAME} (Build #${env.BUILD_NUMBER}) was ABORTED.

                    View build details: ${env.BUILD_URL}

                    Regards,
                    Jenkins CI/CD
                """
            )
        }
    }
}