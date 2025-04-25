/*
 * DevSecOps Pipeline for Windows-based application
 * Includes security scanning and deployment steps
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
  - name: trivy-scanner
    image: aquasec/trivy:latest
    command:
    - powershell
    args:
    - Start-Sleep
    - 999999
    volumeMounts:
    - name: docker-socket
      mountPath: /var/run/docker.sock
  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
  nodeSelector:
    kubernetes.io/os: windows
''') {
    pipeline {
        agent {
            kubernetes {
                yaml podTemplate
                defaultContainer 'shell'
            }
        }
        
        environment {
            DOCKER_IMAGE = 'your-app-image:latest'
            REGISTRY_CREDENTIALS = credentials('docker-registry-credentials')
        }

        stages {
            stage('Checkout') {
                steps {
                    retry(count: 2, conditions: [kubernetesAgent(), nonresumable()]) {
                        checkout scm
                    }
                }
            }

            stage('Security Scan - Dependencies') {
                steps {
                    container('shell') {
                        powershell '''
                            # Install and run dependency checker
                            dotnet restore
                            dotnet list package --vulnerable --include-transitive
                        '''
                    }
                }
            }

            stage('Build') {
                steps {
                    container('shell') {
                        powershell '''
                            # Build application
                            dotnet build --configuration Release
                            # Run tests
                            dotnet test --no-build --configuration Release
                        '''
                    }
                }
            }

            stage('Container Security Scan') {
                steps {
                    container('trivy-scanner') {
                        powershell '''
                            # Scan container image for vulnerabilities
                            trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}
                        '''
                    }
                }
            }

            stage('Deploy') {
                steps {
                    container('shell') {
                        powershell '''
                            # Deploy application
                            kubectl apply -f kubernetes/deployment.yaml
                            kubectl apply -f kubernetes/service.yaml
                        '''
                    }
                }
            }
        }

        post {
            always {
                container('shell') {
                    powershell '''
                        # Clean up resources
                        Get-ChildItem Env: | Sort-Object Name | Format-Table -AutoSize
                    '''
                }
            }
            success {
                container('shell') {
                    powershell 'Write-Host "Pipeline completed successfully!"'
                }
            }
            failure {
                container('shell') {
                    powershell 'Write-Host "Pipeline failed! Check logs for details."'
                }
            }
        }
    }
}