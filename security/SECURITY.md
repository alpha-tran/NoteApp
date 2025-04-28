# Security Setup

This document outlines the security scanning tools and processes in place for this project.

## Security Scanning Tools

### 1. Trivy

[Trivy](https://github.com/aquasecurity/trivy) is used for comprehensive security scanning, including:
- Vulnerability scanning
- Secret detection
- Misconfiguration detection
- License compliance
- Container image scanning

### 2. Pre-commit Hooks

Pre-commit hooks are set up to catch security issues before they're committed:
- [Gitleaks](https://github.com/gitleaks/gitleaks) for secret detection
- [Bandit](https://github.com/PyCQA/bandit) for Python security scanning
- [ESLint](https://eslint.org/) for JavaScript/TypeScript security issues
- Various other code quality checks

### 3. Dependency Scanning

Tools used for scanning dependencies:
- `pip-audit` and `safety` for Python dependencies
- `npm audit` for Node.js dependencies

## Automated Security Scanning

### GitHub Actions Workflow

A GitHub Actions workflow is configured to run security scans automatically:
- Runs on every push to main branch
- Runs on every pull request against main
- Runs weekly on Sunday at midnight
- Uploads results to GitHub Security tab

## Local Security Scanning

### Windows PowerShell Script

The `security-check.ps1` script provides an easy way to run security scans locally on Windows:

```powershell
# Install required tools
.\security-check.ps1 -InstallDependencies

# Run full security scan
.\security-check.ps1 -ScanAll

# Run specific scans
.\security-check.ps1 -ScanVulnerabilities -ScanSecrets

# Output in different formats
.\security-check.ps1 -OutputFormat json -OutputFile results.json
```

### Linux/macOS Shell Script

The `security-check.sh` script provides equivalent functionality for Linux and macOS:

```bash
# Make the script executable
chmod +x security-check.sh

# Install required tools
./security-check.sh --install-dependencies

# Run full security scan
./security-check.sh --scan-all

# Run specific scans
./security-check.sh --scan-vulnerabilities --scan-secrets

# Output in different formats
./security-check.sh --output-format json --output-file results.json
```

## Security Best Practices

### 1. Regular Scanning

- Run security scans weekly at minimum
- Scan before major releases
- Remediate critical issues immediately

### 2. Dependency Management

- Keep dependencies updated
- Review security advisories for dependencies
- Use dependency lockfiles (package-lock.json, requirements.txt with pinned versions)

### 3. Code Review

- Include security review in code review process
- Look for security issues in pull requests
- Use the pre-commit hooks to catch issues early

### 4. Secrets Management

- Never commit secrets to source code
- Use environment variables or secure vaults
- Rotate credentials regularly

## Reporting Security Issues

If you discover a security issue, please report it by sending an email to [security@example.com](mailto:security@example.com).

Please include:
- The steps to reproduce the issue
- The affected component or feature
- Potential impact of the issue
- Any potential mitigations you've identified 