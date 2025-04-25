pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'noteapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        CODACY_PROJECT_TOKEN = credentials('codacy-project-token')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install coverage codacy-coverage'
            }
        }
        
        stage('Run Tests with Coverage') {
            steps {
                sh 'coverage run -m pytest'
                sh 'coverage xml'
            }
        }
        
        stage('Upload Coverage to Codacy') {
            steps {
                sh 'python-codacy-coverage -r coverage.xml'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    // Run Codacy analysis
                    sh 'curl -fsSL https://coverage.codacy.com/get.sh | bash -s -- report -r coverage.xml'
                }
            }
        }
    }
    
    post {
        always {
            // Clean up
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 