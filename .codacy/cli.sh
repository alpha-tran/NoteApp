#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_message() {
    color=$1
    message=$2
    printf "${color}%s${NC}\n" "$message"
}

# Function to ensure directory exists
ensure_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
    fi
}

# Function to get latest version from GitHub API
get_latest_version() {
    local headers=(-H "Accept: application/vnd.github.v3+json" -H "User-Agent: curl")
    if [ -n "$GH_TOKEN" ]; then
        headers+=(-H "Authorization: Bearer $GH_TOKEN")
    fi
    
    local api_url="https://api.github.com/repos/codacy/codacy-cli-v2/releases/latest"
    local response
    
    if ! response=$(curl -s -f "${headers[@]}" "$api_url"); then
        if [ $? -eq 22 ] && [ "$(curl -s -o /dev/null -w "%{http_code}" "${headers[@]}" "$api_url")" -eq 403 ]; then
            print_message "$RED" "Error: GitHub API rate limit exceeded. Please try again later or set GH_TOKEN environment variable."
            exit 1
        fi
        print_message "$YELLOW" "Failed to get latest version from GitHub API"
        exit 1
    fi
    
    echo "$response" | grep -o '"tag_name": *"[^"]*"' | cut -d'"' -f4
}

# Function to download file
download_file() {
    local url=$1
    local output=$2
    local headers=(-H "User-Agent: curl")
    
    if [ -n "$GH_TOKEN" ]; then
        headers+=(-H "Authorization: Bearer $GH_TOKEN")
    fi
    
    print_message "$GREEN" "Downloading from URL: $url"
    if ! curl -L -f --progress-bar "${headers[@]}" "$url" -o "$output"; then
        print_message "$RED" "Download failed"
        return 1
    fi
    return 0
}

# Determine OS-specific paths
if [ -n "$CODACY_CLI_V2_TMP_FOLDER" ]; then
    BASE_DIR="$CODACY_CLI_V2_TMP_FOLDER"
else
    if [ "$(uname)" == "Darwin" ]; then
        BASE_DIR="$HOME/Library/Application Support/codacy/cli-v2"
    else
        BASE_DIR="$HOME/.codacy/cli-v2"
    fi
fi

BIN_NAME="codacy-cli-v2"
VERSION_FILE="$BASE_DIR/version.yaml"

# Get or update version
if [ ! -f "$VERSION_FILE" ] || [ "$1" = "update" ]; then
    print_message "$GREEN" "Fetching latest version..."
    VERSION=$(get_latest_version)
    ensure_directory "$BASE_DIR"
    echo "version: \"$VERSION\"" > "$VERSION_FILE"
else
    VERSION=$(grep -o '"[^"]*"' "$VERSION_FILE" | tr -d '"' | tail -1)
    if [ -z "$VERSION" ]; then
        print_message "$RED" "Invalid version file format"
        exit 1
    fi
fi

# Override version if environment variable is set
if [ -n "$CODACY_CLI_V2_VERSION" ]; then
    VERSION="$CODACY_CLI_V2_VERSION"
    print_message "$YELLOW" "Using version from environment: $VERSION"
fi

# Set up paths
BIN_FOLDER="$BASE_DIR/$VERSION"
BIN_PATH="$BIN_FOLDER/$BIN_NAME"

# Download CLI if needed
if [ ! -f "$BIN_PATH" ]; then
    ensure_directory "$BIN_FOLDER"
    
    # Determine architecture
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64)  ARCH="amd64" ;;
        aarch64) ARCH="arm64" ;;
        *)       ARCH="386" ;;
    esac
    
    # Determine OS
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    case "$OS" in
        darwin) OS="darwin" ;;
        linux)  OS="linux" ;;
        *)      print_message "$RED" "Unsupported operating system: $OS"; exit 1 ;;
    esac
    
    DOWNLOAD_URL="https://github.com/codacy/codacy-cli-v2/releases/download/$VERSION/${BIN_NAME}_${VERSION}_${OS}_${ARCH}.tar.gz"
    TAR_FILE="$BIN_FOLDER/cli.tar.gz"
    
    if ! download_file "$DOWNLOAD_URL" "$TAR_FILE"; then
        exit 1
    fi
    
    if ! tar -xzf "$TAR_FILE" -C "$BIN_FOLDER"; then
        print_message "$RED" "Failed to extract CLI"
        rm -f "$TAR_FILE"
        exit 1
    fi
    
    rm -f "$TAR_FILE"
    chmod +x "$BIN_PATH"
fi

if [ "$#" -eq 1 ] && [ "$1" = "download" ]; then
    print_message "$GREEN" "Codacy CLI v2 download succeeded"
else
    if ! "$BIN_PATH" "$@"; then
        exit $?
    fi
fi