# PowerShell script to download and set up Codacy Analysis CLI v2 for Windows

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Function to ensure directory exists
function Ensure-Directory($path) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# Function to get latest release version from GitHub API
function Get-LatestVersion {
    try {
        $headers = @{
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "PowerShell"
        }
        if ($env:GH_TOKEN) {
            $headers["Authorization"] = "Bearer $env:GH_TOKEN"
        }
        $apiUrl = "https://api.github.com/repos/codacy/codacy-cli-v2/releases/latest"
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers
        return $response.tag_name
    } catch {
        if ($_.Exception.Response.StatusCode -eq 403) {
            Write-ColorOutput Red "Error: GitHub API rate limit exceeded. Please try again later or set GH_TOKEN environment variable."
            exit 1
        }
        Write-ColorOutput Yellow "Failed to get latest version from GitHub API: $_"
        exit 1
    }
}

# Function to download file with progress
function Download-FileWithProgress {
    param (
        [string]$Url,
        [string]$OutFile
    )
    
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.Add("User-Agent", "PowerShell")
        if ($env:GH_TOKEN) {
            $webClient.Headers.Add("Authorization", "Bearer $env:GH_TOKEN")
        }
        
        Write-ColorOutput Green "Downloading from URL: $Url"
        $webClient.DownloadFile($Url, $OutFile)
        return $true
    } catch {
        Write-ColorOutput Red "Download failed: $_"
        return $false
    } finally {
        if ($webClient) {
            $webClient.Dispose()
        }
    }
}

# Set TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Variables
$binName = "codacy-cli-v2"
if ($env:CODACY_CLI_V2_TMP_FOLDER) {
    $baseDir = $env:CODACY_CLI_V2_TMP_FOLDER
} else {
    $baseDir = Join-Path $env:USERPROFILE ".codacy\cli-v2"
}
$versionFile = Join-Path $baseDir "version.yaml"

# Get or update version
if (-not (Test-Path $versionFile) -or $args[0] -eq "update") {
    Write-ColorOutput Green "Fetching latest version..."
    $version = Get-LatestVersion
    Ensure-Directory $baseDir
    Set-Content -Path $versionFile -Value "version: `"$version`"" -Encoding UTF8
} else {
    $versionContent = Get-Content $versionFile -Raw
    if ($versionContent -match 'version: *"([^"]*)"') {
        $version = $matches[1]
    } else {
        Write-ColorOutput Red "Invalid version file format"
        exit 1
    }
}

# Override version if environment variable is set
if ($env:CODACY_CLI_V2_VERSION) {
    $version = $env:CODACY_CLI_V2_VERSION
    Write-ColorOutput Yellow "Using version from environment: $version"
}

# Set up paths
$binFolder = Join-Path $baseDir $version
$binPath = Join-Path $binFolder "$binName.exe"

# Download CLI if needed
if (-not (Test-Path $binPath)) {
    Ensure-Directory $binFolder
    $arch = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "386" }
    $downloadUrl = "https://github.com/codacy/codacy-cli-v2/releases/download/$version/$binName`_$version`_windows_$arch.tar.gz"
    $tarFile = Join-Path $binFolder "cli.tar.gz"
    
    if (-not (Download-FileWithProgress -Url $downloadUrl -OutFile $tarFile)) {
        exit 1
    }
    
    try {
        tar -xzf $tarFile -C $binFolder
        Remove-Item $tarFile -Force
    } catch {
        Write-ColorOutput Red "Failed to extract CLI: $_"
        exit 1
    }
}

if ($args.Count -eq 1 -and $args[0] -eq "download") {
    Write-ColorOutput Green "Codacy CLI v2 download succeeded"
} else {
    try {
        & $binPath $args
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    } catch {
        Write-ColorOutput Red "Failed to execute CLI: $_"
        exit 1
    }
} 