pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'noteapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        CODACY_PROJECT_TOKEN = credentials('codacy-project-token')
        DOCKER_REGISTRY = credentials('docker-registry-url')
        DOCKER_CREDENTIALS_ID = credentials('docker-credentials-id')
        KUBECONFIG_CREDENTIALS_ID = credentials('kubeconfig-credentials-id')
        NODE_ENV = 'production'
        ENVIRONMENT = 'production'
    }
    
    stages {
        stage('Environment Validation') {
            steps {
                script {
                    try {
                        // Validate required credentials
                        if (!DOCKER_REGISTRY || !DOCKER_CREDENTIALS_ID || !KUBECONFIG_CREDENTIALS_ID) {
                            error "Missing required credentials"
                        }
                        
                        // Check for required tools
                        bat '''
                            echo Checking Python version...
                            python --version
                            echo Checking Docker version...
                            docker --version
                            echo Checking kubectl version...
                            kubectl version --client
                            echo Checking npm version...
                            npm --version
                        '''
                    } catch (Exception e) {
                        error "Environment validation failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    try {
                        bat '''
                            echo Creating Python virtual environment...
                            if exist venv rmdir /s /q venv
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip setuptools wheel
                        '''
                    } catch (Exception e) {
                        error "Failed to setup Python environment: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    try {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            echo Installing security tools...
                            pip install bandit safety
                            echo Running Bandit security scan...
                            bandit -r backend/app -f json -o bandit-results.json
                            echo Running Safety check...
                            safety check -r backend/requirements.txt --json > safety-results.json
                        '''
                        
                        dir('frontend') {
                            bat '''
                                echo Running npm audit...
                                npm audit --json > npm-audit.json
                            '''
                        }
                    } catch (Exception e) {
                        error "Security scan failed: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Build Backend') {
            steps {
                script {
                    dir('backend') {
                        bat '''
                            echo Setting up backend environment...
                            IF NOT EXIST venv (
                                python -m venv venv
                            )
                            call venv\\Scripts\\activate.bat
                            echo Installing backend dependencies...
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt --no-cache-dir
                            pip install pytest pytest-cov --no-cache-dir
                        '''
                    }
                }
            }
        }
        
        stage('Build Frontend') {
            steps {
                dir('frontend') {
                    bat '''
                        echo Installing frontend dependencies...
                        npm install
                        echo Building frontend...
                        npm run build
                    '''
                }
            }
        }
        
        stage('Test Backend') {
            steps {
                script {
                    try {
                        dir('backend') {
                            bat '''
                                echo Running backend tests...
                                call venv\\Scripts\\activate.bat
                                python -m pytest tests/ --cov=app --cov-report=xml --junitxml=test-results.xml
                            '''
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
                            bat '''
                                echo Running frontend tests...
                                npm test -- --watchAll=false --ci --coverage --reporters=default --reporters=jest-junit
                            '''
                        }
                    } catch (Exception e) {
                        error "Failed to test frontend: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Code Quality Analysis') {
            steps {
                script {
                    try {
                        bat '''
                            echo Running Codacy analysis...
                            call venv\\Scripts\\activate.bat
                            pip install codacy-coverage
                            python-codacy-coverage -r backend/coverage.xml
                            npx codacy-coverage < frontend/coverage/lcov.info
                        '''
                    } catch (Exception e) {
                        error "Code quality analysis failed: ${e.getMessage()}"
                    }
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                bat '''
                    echo Building Docker images...
                    docker build -t alpha-tran/noteapp-backend:latest .\\backend
                    docker build -t alpha-tran/noteapp-frontend:latest .\\frontend
                '''
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                bat '''
                    echo Deploying to Kubernetes...
                    kubectl apply -f k8s\\backend-deployment.yaml
                    kubectl apply -f k8s\\frontend-deployment.yaml
                '''
            }
        }
    }
    
    post {
        success {
            script {
                currentBuild.description = "Build and deployment successful"
                emailext (
                    subject: "Pipeline '${currentBuild.fullDisplayName}' SUCCESSFUL",
                    body: "Build completed successfully\n\nCheck console output at ${BUILD_URL}",
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                )
            }
        }
        failure {
            script {
                currentBuild.description = "Build failed: ${currentBuild.description}"
                emailext (
                    subject: "Pipeline '${currentBuild.fullDisplayName}' FAILED",
                    body: "Build failed\n\nCheck console output at ${BUILD_URL}",
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                )
            }
        }
        always {
            script {
                try {
                    bat '''
                        echo Cleaning up...
                        if exist venv rmdir /s /q venv
                        docker system prune -f
                    '''
                } catch (Exception e) {
                    echo "Warning: Cleanup failed: ${e.getMessage()}"
                }
                
                archiveArtifacts artifacts: '''
                    **/test-results.xml,
                    **/coverage.xml,
                    **/bandit-results.json,
                    **/safety-results.json,
                    **/npm-audit.json
                ''', allowEmptyArchive: true
                junit '**/test-results.xml'
            }
        }
    }
} 