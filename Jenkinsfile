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
                script {
                    // Ensure correct line endings on Windows
                    if (IS_WINDOWS == 'true') {
                        bat 'git config --global core.autocrlf true'
                    }
                }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    try {
                        if (IS_WINDOWS == 'true') {
                            bat 'python -V'
                            bat 'if exist venv rmdir /s /q venv'
                            bat 'python -m venv venv'
                            bat '.\\venv\\Scripts\\activate && python -m pip install --upgrade pip setuptools wheel'
                        } else {
                            sh 'python3 -V'
                            sh 'rm -rf venv'
                            sh 'python3 -m venv venv'
                            sh '. venv/bin/activate && pip3 install --upgrade pip setuptools wheel'
                        }
                    } catch (Exception e) {
                        error "Failed to setup Python environment: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Build Backend') {
            steps {
                script {
                    try {
                        dir('backend') {
                            if (IS_WINDOWS == 'true') {
                                bat '''
                                    call ..\\venv\\Scripts\\activate
                                    echo "Installing dependencies..."
                                    python -m pip install -r requirements.txt --no-cache-dir
                                    python -m pip install pytest pytest-cov --no-cache-dir
                                '''
                            } else {
                                sh '''
                                    . ../venv/bin/activate
                                    echo "Installing dependencies..."
                                    pip3 install -r requirements.txt --no-cache-dir
                                    pip3 install pytest pytest-cov --no-cache-dir
                                '''
                            }
                        }
                    } catch (Exception e) {
                        error "Failed to build backend: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                script {
                    try {
                        dir('frontend') {
                            if (IS_WINDOWS == 'true') {
                                bat 'npm install'
                                bat 'npm run build'
                            } else {
                                sh 'npm install'
                                sh 'npm run build'
                            }
                        }
                    } catch (Exception e) {
                        error "Failed to build frontend: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Test Backend') {
            steps {
                script {
                    try {
                        dir('backend') {
                            if (IS_WINDOWS == 'true') {
                                bat '''
                                    call ..\\venv\\Scripts\\activate
                                    python -m pytest tests/ --cov=app --cov-report=xml
                                '''
                            } else {
                                sh '''
                                    . ../venv/bin/activate
                                    python -m pytest tests/ --cov=app --cov-report=xml
                                '''
                            }
                        }
                    } catch (Exception e) {
                        error "Failed to test backend: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Test Frontend') {
            steps {
                script {
                    try {
                        dir('frontend') {
                            if (IS_WINDOWS == 'true') {
                                bat 'npm test -- --watchAll=false'
                            } else {
                                sh 'npm test -- --watchAll=false'
                            }
                        }
                    } catch (Exception e) {
                        error "Failed to test frontend: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    try {
                        if (IS_WINDOWS == 'true') {
                            bat "docker build -t ${DOCKER_REGISTRY}/frontend:${BUILD_NUMBER} ./frontend"
                            bat "docker build -t ${DOCKER_REGISTRY}/backend:${BUILD_NUMBER} ./backend"
                        } else {
                            sh "docker build -t ${DOCKER_REGISTRY}/frontend:${BUILD_NUMBER} ./frontend"
                            sh "docker build -t ${DOCKER_REGISTRY}/backend:${BUILD_NUMBER} ./backend"
                        }
                    } catch (Exception e) {
                        error "Failed to build Docker images: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                script {
                    try {
                        if (IS_WINDOWS == 'true') {
                            bat 'kubectl apply -f k8s/'
                        } else {
                            sh 'kubectl apply -f k8s/'
                        }
                    } catch (Exception e) {
                        error "Failed to deploy to K8s: ${e.getMessage()}"
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
                // Cleanup
                try {
                    if (IS_WINDOWS == 'true') {
                        bat 'if exist venv rmdir /s /q venv'
                    } else {
                        sh 'rm -rf venv'
                    }
                } catch (Exception e) {
                    echo "Warning: Cleanup failed: ${e.getMessage()}"
                }
            }
        }
    }
} 