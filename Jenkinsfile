pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'noteapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
        CODACY_PROJECT_TOKEN = credentials('codacy-project-token')
        DOCKER_REGISTRY = credentials('docker-registry-url')
        DOCKER_CREDENTIALS_ID = credentials('docker-credentials-id')
        KUBECONFIG_CREDENTIALS_ID = credentials('kubeconfig-credentials-id')
        // Determine OS-specific commands
        IS_WINDOWS = isUnix() ? 'false' : 'true'
        PIP_CMD = isUnix() ? 'pip3' : 'python -m pip'
        VENV_CMD = isUnix() ? 'python3 -m venv' : 'python -m venv'
        ACTIVATE_CMD = isUnix() ? 'source venv/bin/activate' : '.\\venv\\Scripts\\activate'
        // Environment variables for application
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
                            python --version
                            docker --version
                            kubectl version --client
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
                git branch: 'main', url: 'https://github.com/alpha-tran/NoteApp.git'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    try {
                        bat '''
                            if exist venv rmdir /s /q venv
                            python -m venv venv
                            call venv\\Scripts\\activate
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
                        // Install and run security scanning tools
                        bat '''
                            call venv\\Scripts\\activate
                            pip install bandit safety
                            bandit -r backend/app -f json -o bandit-results.json
                            safety check -r backend/requirements.txt --json > safety-results.json
                        '''
                        
                        // Run npm audit for frontend
                        dir('frontend') {
                            bat 'npm audit --json > npm-audit.json'
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
                            IF NOT EXIST venv (
                                python -m venv venv
                            )
                            call venv\\Scripts\\activate.bat
                            echo "Installing dependencies..."
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
                    bat 'npm install'
                    bat 'npm run build'
                }
            }
        }
        
        stage('Test Backend') {
            steps {
                script {
                    try {
                        dir('backend') {
                            bat '''
                                call ..\\venv\\Scripts\\activate
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
                            bat 'npm test -- --watchAll=false --ci --coverage --reporters=default --reporters=jest-junit'
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
                        // Run Codacy analysis
                        bat '''
                            call venv\\Scripts\\activate
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
                bat 'docker build -t alpha-tran/noteapp-backend:latest .\\backend'
                bat 'docker build -t alpha-tran/noteapp-frontend:latest .\\frontend'
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                bat 'kubectl apply -f k8s\\backend-deployment.yaml'
                bat 'kubectl apply -f k8s\\frontend-deployment.yaml'
            }
        }
    }
    
    post {
        success {
            script {
                currentBuild.description = "Build and deployment successful"
                // Send success notification
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
                // Send failure notification
                emailext (
                    subject: "Pipeline '${currentBuild.fullDisplayName}' FAILED",
                    body: "Build failed\n\nCheck console output at ${BUILD_URL}",
                    recipientProviders: [[$class: 'DevelopersRecipientProvider']]
                )
            }
        }
        always {
            script {
                // Cleanup
                try {
                    bat '''
                        if exist venv rmdir /s /q venv
                        docker system prune -f
                    '''
                } catch (Exception e) {
                    echo "Warning: Cleanup failed: ${e.getMessage()}"
                }
                
                // Archive test results and artifacts
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