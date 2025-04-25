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
                git branch: 'feature', url: 'https://github.com/alpha-tran/NoteApp.git'
            }
        }
        
        stage('Setup Environment') {
            parallel {
                stage('Setup Frontend') {
                    steps {
                        dir('frontend') {
                            bat 'npm install'
                        }
                    }
                }
                stage('Setup Backend') {
                    steps {
                        dir('backend') {
                            bat 'pip install -r requirements.txt'
                        }
                    }
                }
            }
        }
        
        stage('Testing') {
            parallel {
                stage('Test Frontend') {
                    steps {
                        dir('frontend') {
                            bat 'npm test -- --watchAll=false'
                        }
                    }
                }
                stage('Test Backend') {
                    steps {
                        dir('backend') {
                            bat 'pytest'
                        }
                    }
                }
            }
        }
        
        stage('Codacy Security Scan') {
            steps {
                echo "Codacy analysis will run automatically on commit/PR or via CLI/plugin"
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Frontend') {
                    steps {
                        dir('frontend') {
                            script {
                                def imageName = "${env.DOCKER_REGISTRY}/noteapp-frontend:${env.BUILD_NUMBER}"
                                bat "docker build -t ${imageName} ."
                            }
                        }
                    }
                }
                stage('Build Backend') {
                    steps {
                        dir('backend') {
                            script {
                                def imageName = "${env.DOCKER_REGISTRY}/noteapp-backend:${env.BUILD_NUMBER}"
                                bat "docker build -t ${imageName} ."
                            }
                        }
                    }
                }
            }
        }
        
        stage('Push Docker Images') {
            steps {
                script {
                    withCredentials([string(credentialsId: env.DOCKER_CREDENTIALS_ID, variable: 'DOCKER_PASSWORD')]) {
                        bat "echo %DOCKER_PASSWORD% | docker login -u ${env.DOCKER_REGISTRY} --password-stdin"
                        bat "docker push ${env.DOCKER_REGISTRY}/noteapp-frontend:${env.BUILD_NUMBER}"
                        bat "docker push ${env.DOCKER_REGISTRY}/noteapp-backend:${env.BUILD_NUMBER}"
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: env.KUBECONFIG_CREDENTIALS_ID, variable: 'KUBECONFIG')]) {
                    bat '''
                        echo "Applying Kubernetes manifests..."
                        kubectl apply -f k8s/
                    '''
                }
                echo "Deployment to Kubernetes (local) initiated."
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
} 