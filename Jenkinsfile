pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'noteapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        CODACY_PROJECT_TOKEN = credentials('codacy-project-token')
        DOCKER_REGISTRY = 'your-docker-registry'
        DOCKER_CREDENTIALS_ID = 'your-docker-credentials-id'
        KUBECONFIG_CREDENTIALS_ID = 'your-kubeconfig-credentials-id'
        // Determine OS-specific commands
        IS_WINDOWS = isUnix() ? 'false' : 'true'
        PIP_CMD = isUnix() ? 'pip3' : 'python -m pip'
        VENV_CMD = isUnix() ? 'python3 -m venv' : 'python -m venv'
        ACTIVATE_CMD = isUnix() ? 'source venv/bin/activate' : '.\\venv\\Scripts\\activate'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/alpha-tran/NoteApp.git'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    if (IS_WINDOWS == 'true') {
                        bat 'python -V'
                        bat 'python -m venv venv'
                        bat '.\\venv\\Scripts\\activate && python -m pip install --upgrade pip'
                    } else {
                        sh 'python3 -V'
                        sh 'python3 -m venv venv'
                        sh 'source venv/bin/activate && pip3 install --upgrade pip'
                    }
                }
            }
        }
        
        stage('Build Backend') {
            steps {
                dir('backend') {
                    script {
                        if (IS_WINDOWS == 'true') {
                            bat '''
                                call ..\\venv\\Scripts\\activate
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install pytest pytest-cov
                            '''
                        } else {
                            sh '''
                                source ../venv/bin/activate
                                pip3 install --upgrade pip
                                pip3 install -r requirements.txt
                                pip3 install pytest pytest-cov
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    script {
                        if (IS_WINDOWS == 'true') {
                            bat 'npm install'
                            bat 'npm run build'
                        } else {
                            sh 'npm install'
                            sh 'npm run build'
                        }
                    }
                }
            }
        }
        
        stage('Test Backend') {
            steps {
                dir('backend') {
                    script {
                        if (IS_WINDOWS == 'true') {
                            bat '''
                                call ..\\venv\\Scripts\\activate
                                python -m pytest tests/ --cov=app --cov-report=xml
                            '''
                        } else {
                            sh '''
                                source ../venv/bin/activate
                                python -m pytest tests/ --cov=app --cov-report=xml
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Test Frontend') {
            steps {
                dir('frontend') {
                    script {
                        if (IS_WINDOWS == 'true') {
                            bat 'npm test -- --watchAll=false'
                        } else {
                            sh 'npm test -- --watchAll=false'
                        }
                    }
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    if (IS_WINDOWS == 'true') {
                        bat "docker build -t ${DOCKER_REGISTRY}/frontend:${BUILD_NUMBER} ./frontend"
                        bat "docker build -t ${DOCKER_REGISTRY}/backend:${BUILD_NUMBER} ./backend"
                    } else {
                        sh "docker build -t ${DOCKER_REGISTRY}/frontend:${BUILD_NUMBER} ./frontend"
                        sh "docker build -t ${DOCKER_REGISTRY}/backend:${BUILD_NUMBER} ./backend"
                    }
                }
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                script {
                    if (IS_WINDOWS == 'true') {
                        bat 'kubectl apply -f k8s/'
                    } else {
                        sh 'kubectl apply -f k8s/'
                    }
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
        always {
            script {
                if (IS_WINDOWS == 'true') {
                    bat 'if exist venv rmdir /s /q venv'
                } else {
                    sh 'rm -rf venv'
                }
            }
        }
    }
} 