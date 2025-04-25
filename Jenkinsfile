pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'noteapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        CODACY_PROJECT_TOKEN = credentials('codacy-project-token')
        DOCKER_REGISTRY = 'your-docker-registry'
        DOCKER_CREDENTIALS_ID = 'your-docker-credentials-id'
        KUBECONFIG_CREDENTIALS_ID = 'your-kubeconfig-credentials-id'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/alpha-tran/NoteApp.git'
            }
        }
        
        stage('Build Backend') {
            steps {
                dir('backend') {
                    bat 'python -m pip install --upgrade pip'
                    bat 'pip install -r requirements.txt'
                    bat 'pip install pytest pytest-cov'
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    bat 'npm install'
                    bat 'npm run build'
                }
            }
        }
        
        stage('Test Backend') {
            steps {
                dir('backend') {
                    bat 'python -m pytest tests/ --cov=app --cov-report=xml'
                }
            }
        }
        
        stage('Test Frontend') {
            steps {
                dir('frontend') {
                    bat 'npm test -- --watchAll=false'
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    bat "docker build -t ${DOCKER_REGISTRY}/frontend:${BUILD_NUMBER} ./frontend"
                    bat "docker build -t ${DOCKER_REGISTRY}/backend:${BUILD_NUMBER} ./backend"
                }
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                script {
                    bat 'kubectl apply -f k8s/'
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline execution failed!'
        }
    }
} 