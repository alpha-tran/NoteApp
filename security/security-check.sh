#!/bin/bash
# Security Scan Shell Script

# Default values
INSTALL_DEPENDENCIES=false
SCAN_VULNERABILITIES=false
SCAN_SECRETS=false
SCAN_DEPENDENCIES=false
SCAN_ALL=false
OUTPUT_FORMAT="table"
OUTPUT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --install-dependencies)
      INSTALL_DEPENDENCIES=true
      shift
      ;;
    --scan-vulnerabilities)
      SCAN_VULNERABILITIES=true
      shift
      ;;
    --scan-secrets)
      SCAN_SECRETS=true
      shift
      ;;
    --scan-dependencies)
      SCAN_DEPENDENCIES=true
      shift
      ;;
    --scan-all)
      SCAN_ALL=true
      shift
      ;;
    --output-format)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --output-file)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Default to scanning all if no specific scan is requested
if [[ "$SCAN_VULNERABILITIES" = false && "$SCAN_SECRETS" = false && "$SCAN_DEPENDENCIES" = false && "$SCAN_ALL" = false ]]; then
  SCAN_ALL=true
fi

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies
install_security_tools() {
  echo -e "\033[0;36mInstalling security scanning tools...\033[0m"
  
  # Check if pip is installed
  if ! command_exists pip; then
    echo -e "\033[0;31mpip is not installed. Please install Python and pip first.\033[0m"
    exit 1
  fi
  
  # Install Python security tools
  echo -e "\033[0;36mInstalling Python security tools...\033[0m"
  pip install safety pip-audit bandit
  
  # Check if npm is installed
  if command_exists npm; then
    echo -e "\033[0;36mInstalling npm security tools...\033[0m"
    npm install -g npm-audit-resolver
  fi
  
  # Check if Docker is installed for Trivy
  if ! command_exists docker; then
    echo -e "\033[0;33mDocker is not installed. Please install Docker to use Trivy scanner.\033[0m"
  else
    echo -e "\033[0;36mPulling latest Trivy Docker image...\033[0m"
    docker pull aquasec/trivy
  fi
  
  # Install pre-commit
  echo -e "\033[0;36mInstalling pre-commit hooks...\033[0m"
  pip install pre-commit
  pre-commit install
  
  echo -e "\033[0;32mSecurity tools installation complete!\033[0m"
}

# Function to scan for vulnerabilities using Trivy
scan_vulnerabilities() {
  echo -e "\033[0;36mScanning for vulnerabilities...\033[0m"
  
  if ! command_exists docker; then
    echo -e "\033[0;31mDocker is not installed. Please install Docker to use Trivy scanner.\033[0m"
    return
  fi
  
  FORMAT=$OUTPUT_FORMAT
  if [[ -n "$OUTPUT_FILE" ]]; then
    OUTPUT_ARG="--output $OUTPUT_FILE"
  else
    OUTPUT_ARG=""
  fi
  
  CMD="docker run --rm -v $(pwd):/src aquasec/trivy fs --security-checks vuln --severity CRITICAL,HIGH,MEDIUM --format $FORMAT $OUTPUT_ARG /src"
  echo -e "\033[0;90mRunning: $CMD\033[0m"
  eval $CMD
  
  echo -e "\033[0;32mVulnerability scan complete!\033[0m"
}

# Function to scan for secrets
scan_secrets() {
  echo -e "\033[0;36mScanning for secrets...\033[0m"
  
  if ! command_exists docker; then
    echo -e "\033[0;31mDocker is not installed. Please install Docker to use Trivy scanner.\033[0m"
    return
  fi
  
  FORMAT=$OUTPUT_FORMAT
  if [[ -n "$OUTPUT_FILE" ]]; then
    OUTPUT_ARG="--output $OUTPUT_FILE"
  else
    OUTPUT_ARG=""
  fi
  
  CMD="docker run --rm -v $(pwd):/src aquasec/trivy fs --security-checks secret --format $FORMAT $OUTPUT_ARG /src"
  echo -e "\033[0;90mRunning: $CMD\033[0m"
  eval $CMD
  
  echo -e "\033[0;32mSecret scan complete!\033[0m"
}

# Function to scan dependencies
scan_dependencies() {
  echo -e "\033[0;36mScanning dependencies...\033[0m"
  
  # Check for Python dependencies
  if [[ -f "requirements.txt" ]]; then
    echo -e "\033[0;36mScanning Python dependencies...\033[0m"
    if command_exists pip-audit; then
      pip-audit -r requirements.txt
    elif command_exists safety; then
      safety check -r requirements.txt
    else
      echo -e "\033[0;33mNo Python security scanner found. Please run with --install-dependencies flag.\033[0m"
    fi
  fi
  
  # Check for Node.js dependencies
  if [[ -f "package.json" ]]; then
    echo -e "\033[0;36mScanning Node.js dependencies...\033[0m"
    if command_exists npm; then
      npm audit
    else
      echo -e "\033[0;33mnpm not found. Cannot scan Node.js dependencies.\033[0m"
    fi
  fi
  
  echo -e "\033[0;32mDependency scan complete!\033[0m"
}

# Main execution
{
  # Install dependencies if requested
  if [[ "$INSTALL_DEPENDENCIES" = true ]]; then
    install_security_tools
  fi
  
  # Run scans based on parameters
  if [[ "$SCAN_ALL" = true || "$SCAN_VULNERABILITIES" = true ]]; then
    scan_vulnerabilities
  fi
  
  if [[ "$SCAN_ALL" = true || "$SCAN_SECRETS" = true ]]; then
    scan_secrets
  fi
  
  if [[ "$SCAN_ALL" = true || "$SCAN_DEPENDENCIES" = true ]]; then
    scan_dependencies
  fi
  
  echo -e "\033[0;32mSecurity scan completed successfully!\033[0m"
} || {
  echo -e "\033[0;31mError during security scan!\033[0m"
  exit 1
} 