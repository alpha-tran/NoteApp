/*
 * DevSecOps Pipeline for NoteApp on Windows pod
 * Includes frontend, backend, and security scanning stages
 */
podTemplate(yaml: '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:windowsservercore-1809
  - name: shell
    image: mcr.microsoft.com/powershell:preview-windowsservercore-1809
    command:
    - powershell
    args:
    - Start-Sleep
    - 999999
  - name: python
    image: python:3.9-windowsservercore-1809
    command:
    - powershell
    args:
    - Start-Sleep
    - 999999
  - name: node
    image: node:16-windowsservercore-1809
    command:
    - powershell
    args:
    - Start-Sleep
    - 999999
  - name: docker
    image: docker:20.10-windowsservercore-1809
    command:
    - powershell
    args:
    - Start-Sleep
    - 999999
    volumeMounts:
    - name: docker-sock
      mountPath: \\\\.\\pipe\\docker_engine
  volumes:
  - name: docker-sock
    hostPath:
      path: \\\\.\\pipe\\docker_engine
  nodeSelector:
    kubernetes.io/os: windows
''') {
    retry(count: 2, conditions: [kubernetesAgent(), nonresumable()]) {
        node(POD_LABEL) {
            stage('Checkout') {
                checkout scm
            }

            stage('Security Scan') {
                container('python') {
                    powershell '''
                        python -m pip install --upgrade pip
                        pip install bandit safety
                        bandit -r backend/app -f json -o bandit-results.json
                        safety check -r backend/requirements.txt --json > safety-results.json
                    '''
                }
                container('node') {
                    powershell '''
                        cd frontend
                        npm install
                        npm audit --json > npm-audit.json
                    '''
                }
            }

            stage('Build Backend') {
                container('python') {
                    powershell '''
                        cd backend
                        python -m venv venv
                        .\\venv\\Scripts\\Activate.ps1
                        pip install -r requirements.txt
                        pip install pytest pytest-cov
                        pytest tests/ --cov=app --cov-report=xml --junitxml=test-results.xml
                    '''
                }
            }

            stage('Build Frontend') {
                container('node') {
                    powershell '''
                        cd frontend
                        npm install
                        npm run build
                        npm test -- --watchAll=false --ci --coverage
                    '''
                }
            }

            stage('Build Docker Images') {
                container('docker') {
                    powershell '''
                        cd backend
                        docker build -t alpha-tran/noteapp-backend:latest .
                        cd ../frontend
                        docker build -t alpha-tran/noteapp-frontend:latest .
                    '''
                }
            }

            stage('Deploy') {
                container('shell') {
                    powershell '''
                        kubectl apply -f k8s/backend-deployment.yaml
                        kubectl apply -f k8s/frontend-deployment.yaml
                    '''
                }
            }
        }
    }
} 