#!/bin/bash

set -e  # Exit on any error

# Function to show critical error popups
show_critical_error() {
    local message="$1"
    if command -v zenity &>/dev/null; then
        zenity --error --title="YouTube Downloader - Critical Error" --text="$message" --width=300 --timeout=10 2>/dev/null || true
    else
        echo "CRITICAL: $message"
    fi
}

# Function to check internet connection
check_internet() {
    ping -c 1 google.com &>/dev/null
}

# Helper to install a package if missing
install_if_missing() {
    local cmd=$1
    local pkg=$2
    local critical=$3

    if ! command -v "$cmd" &>/dev/null; then
        if check_internet; then
            sudo apt update && sudo apt install -y "$pkg" || {
                [ "$critical" = true ] && show_critical_error "$cmd could not be installed." && exit 1
                return 1
            }
        else
            [ "$critical" = true ] && show_critical_error "$cmd is required and cannot be installed without internet." && exit 1
            return 1
        fi
    fi
    return 0
}

# Check for Zenity (non-critical)
command -v zenity &>/dev/null || {
    if check_internet; then
        sudo apt install -y zenity || true
    fi
}

# Critical dependencies
install_if_missing python3 python3 true

# Optional dependencies
if check_internet; then
    install_if_missing git git false
    install_if_missing pip python3-pip false
    install_if_missing curl curl false

    if ! command -v poetry &>/dev/null; then
        curl -sSL https://install.python-poetry.org | python3 - || true
        export PATH="$HOME/.local/bin:$PATH"
    fi

    # Git repo update
    if [ -d ".git" ]; then
        git fetch && {
            LOCAL=$(git rev-parse @)
            REMOTE=$(git rev-parse @{u})
            [ "$LOCAL" != "$REMOTE" ] && git pull
        }
    fi

    # Update dependencies
    if command -v poetry &>/dev/null; then
        poetry update || true
    fi
fi

# Launch application
if command -v poetry &>/dev/null; then
    poetry run python youtube_downloader/main.py || {
        show_critical_error "Failed to launch via Poetry."
        python3 youtube_downloader/main.py || show_critical_error "Application failed to start."
    }
else
    python3 youtube_downloader/main.py || show_critical_error "Application failed to start."
fi
