# Security Scan PowerShell Script
param (
    [switch]$InstallDependencies,
    [switch]$ScanVulnerabilities,
    [switch]$ScanSecrets,
    [switch]$ScanDependencies,
    [switch]$ScanAll,
    [string]$OutputFormat = "table",
    [string]$OutputFile
)

# Set the error action preference
$ErrorActionPreference = "Stop"

# Default to scanning all if no specific scan is requested
if (-not ($ScanVulnerabilities -or $ScanSecrets -or $ScanDependencies)) {
    $ScanAll = $true
}

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Function to install dependencies
function Install-SecurityTools {
    Write-Host "Installing security scanning tools..." -ForegroundColor Cyan
    
    # Check if pip is installed
    if (-not (Test-CommandExists "pip")) {
        Write-Host "pip is not installed. Please install Python and pip first." -ForegroundColor Red
        exit 1
    }
    
    # Install Python security tools
    Write-Host "Installing Python security tools..." -ForegroundColor Cyan
    pip install safety pip-audit bandit
    
    # Check if npm is installed
    if (Test-CommandExists "npm") {
        Write-Host "Installing npm security tools..." -ForegroundColor Cyan
        npm install -g npm-audit-resolver
    }
    
    # Check if Docker is installed for Trivy
    if (-not (Test-CommandExists "docker")) {
        Write-Host "Docker is not installed. Please install Docker to use Trivy scanner." -ForegroundColor Yellow
    } else {
        Write-Host "Pulling latest Trivy Docker image..." -ForegroundColor Cyan
        docker pull aquasec/trivy
    }
    
    # Install pre-commit
    Write-Host "Installing pre-commit hooks..." -ForegroundColor Cyan
    pip install pre-commit
    pre-commit install
    
    Write-Host "Security tools installation complete!" -ForegroundColor Green
}

# Function to scan for vulnerabilities using Trivy
function Scan-Vulnerabilities {
    Write-Host "Scanning for vulnerabilities..." -ForegroundColor Cyan
    
    if (-not (Test-CommandExists "docker")) {
        Write-Host "Docker is not installed. Please install Docker to use Trivy scanner." -ForegroundColor Red
        return
    }
    
    $format = if ($OutputFile) { $OutputFormat } else { "table" }
    $outputArg = if ($OutputFile) { "--output $OutputFile" } else { "" }
    
    $cmd = "docker run --rm -v ${PWD}:/src aquasec/trivy fs --security-checks vuln --severity CRITICAL,HIGH,MEDIUM --format $format $outputArg /src"
    Write-Host "Running: $cmd" -ForegroundColor DarkGray
    Invoke-Expression $cmd
    
    Write-Host "Vulnerability scan complete!" -ForegroundColor Green
}

# Function to scan for secrets
function Scan-Secrets {
    Write-Host "Scanning for secrets..." -ForegroundColor Cyan
    
    if (-not (Test-CommandExists "docker")) {
        Write-Host "Docker is not installed. Please install Docker to use Trivy scanner." -ForegroundColor Red
        return
    }
    
    $format = if ($OutputFile) { $OutputFormat } else { "table" }
    $outputArg = if ($OutputFile) { "--output $OutputFile" } else { "" }
    
    $cmd = "docker run --rm -v ${PWD}:/src aquasec/trivy fs --security-checks secret --format $format $outputArg /src"
    Write-Host "Running: $cmd" -ForegroundColor DarkGray
    Invoke-Expression $cmd
    
    Write-Host "Secret scan complete!" -ForegroundColor Green
}

# Function to scan dependencies
function Scan-Dependencies {
    Write-Host "Scanning dependencies..." -ForegroundColor Cyan
    
    # Check for Python dependencies
    if (Test-Path "requirements.txt") {
        Write-Host "Scanning Python dependencies..." -ForegroundColor Cyan
        if (Test-CommandExists "pip-audit") {
            pip-audit -r requirements.txt
        } elseif (Test-CommandExists "safety") {
            safety check -r requirements.txt
        } else {
            Write-Host "No Python security scanner found. Please run with -InstallDependencies flag." -ForegroundColor Yellow
        }
    }
    
    # Check for Node.js dependencies
    if (Test-Path "package.json") {
        Write-Host "Scanning Node.js dependencies..." -ForegroundColor Cyan
        if (Test-CommandExists "npm") {
            npm audit
        } else {
            Write-Host "npm not found. Cannot scan Node.js dependencies." -ForegroundColor Yellow
        }
    }
    
    Write-Host "Dependency scan complete!" -ForegroundColor Green
}

# Main execution
try {
    # Install dependencies if requested
    if ($InstallDependencies) {
        Install-SecurityTools
    }
    
    # Run scans based on parameters
    if ($ScanAll -or $ScanVulnerabilities) {
        Scan-Vulnerabilities
    }
    
    if ($ScanAll -or $ScanSecrets) {
        Scan-Secrets
    }
    
    if ($ScanAll -or $ScanDependencies) {
        Scan-Dependencies
    }
    
    Write-Host "Security scan completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error during security scan: $_" -ForegroundColor Red
    exit 1
} 