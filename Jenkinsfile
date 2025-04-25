pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'user-auth-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r backend/requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'cd backend && pytest tests/'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
            }
        }

        stage('Security Scan') {
            steps {
                sh 'docker scan ${DOCKER_IMAGE}:${DOCKER_TAG}'
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'staging'
            }
            steps {
                sh 'docker push ${DOCKER_IMAGE}:${DOCKER_TAG}'
                // Add deployment steps for staging environment
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker push ${DOCKER_IMAGE}:${DOCKER_TAG}'
                // Add deployment steps for production environment
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
} 