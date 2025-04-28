# Security Check Script for Windows
Write-Host "Running security checks..."

# Check Python dependencies
Write-Host "Checking Python dependencies..."
pip-audit

# Check Node.js dependencies
Write-Host "Checking Node.js dependencies..."
npm audit

# Run Trivy scan
Write-Host "Running Trivy container scan..."
trivy filesystem .

# Run Codacy analysis
Write-Host "Running Codacy analysis..."
./.codacy/cli.ps1 analyze

# Check for sensitive files
Write-Host "Checking for sensitive files..."
$sensitivePatterns = @(
    "*.key",
    "*.pem",
    "*.pfx",
    "*.p12",
    "*.pkcs12",
    "*.password",
    "*.secret"
)

foreach ($pattern in $sensitivePatterns) {
    $files = Get-ChildItem -Path . -Recurse -File -Filter $pattern
    if ($files) {
        Write-Host "WARNING: Found sensitive files matching pattern $pattern:"
        $files | ForEach-Object { Write-Host $_.FullName }
    }
}

# Check for environment files
Write-Host "Checking environment files..."
$envFiles = Get-ChildItem -Path . -Recurse -File -Filter ".env*"
foreach ($file in $envFiles) {
    Write-Host "Found environment file: $($file.FullName)"
    if (Select-String -Path $file.FullName -Pattern "password|secret|key|token" -Quiet) {
        Write-Host "WARNING: Environment file may contain sensitive data: $($file.FullName)"
    }
}

Write-Host "Security check completed." 