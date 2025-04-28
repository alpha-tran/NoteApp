#!/bin/bash

# Update package list
apt-get update
apt-get install -y curl wget apt-transport-https gnupg lsb-release

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list
apt-get update
apt-get install -y trivy

# Install OWASP ZAP
docker pull owasp/zap2docker-stable

# Install SonarQube Scanner
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
unzip sonar-scanner-cli-4.8.0.2856-linux.zip
mv sonar-scanner-4.8.0.2856-linux /opt/sonar-scanner
ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

# Install additional dependencies
apt-get install -y python3-pip nodejs npm
pip3 install pre-commit yamllint
npm install -g eslint prettier

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/* 