pipeline {
    agent any
    environment {
        NODE_ENV = 'development'
        FRONTEND_DIR = 'frontend'
        BACKEND_DIR = 'backend'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh """
                    cd ${FRONTEND_DIR} && npm install
                    cd ../${BACKEND_DIR} && npm install
                """
            }
        }
        stage('Lint & Format') {
            steps {
                sh """
                    cd ${FRONTEND_DIR} && npm run lint
                    cd ../${BACKEND_DIR} && npm run lint
                """
            }
        }
        stage('Test') {
            steps {
                sh """
                    cd ${FRONTEND_DIR} && npm test
                    cd ../${BACKEND_DIR} && npm test
                """
            }
        }
        stage('Security Analysis') {
            steps {
                sh 'codacy-analysis-cli analyze'
            }
        }
        stage('Build') {
            steps {
                sh """
                    cd ${FRONTEND_DIR} && npm run build
                """
            }
        }
    }
    post {
        always {
            junit '**/test-results.xml'
            archiveArtifacts artifacts: '**/build/**'
        }
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
} 