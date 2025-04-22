#!/bin/bash

set -e  # Exit on any error

# Function to show popup messages
show_popup() {
    local message="$1"
    zenity --info --title="YouTube Downloader" --text="$message" --width=300 --timeout=10 2>/dev/null || \
    echo "Zenity not available. Message: $message"
}

# Function to check internet connection
check_internet() {
    if ! ping -c 1 google.com &>/dev/null; then
        show_popup "🌐 No internet connection detected.\nSome features may be limited."
        return 1
    fi
    return 0
}

# Helper to install a package if missing
install_if_missing() {
    local cmd=$1
    local pkg=$2
    local critical=$3

    if ! command -v "$cmd" &>/dev/null; then
        if check_internet; then
            show_popup "🔧 Installing missing requirement: $pkg"
            sudo apt update && sudo apt install -y "$pkg"
        else
            # Show message only if internet is not available
            if ! check_internet; then
                show_popup "⚠️  Critical error: $cmd not found\nand cannot install without internet"
                [ "$critical" = true ] && exit 1
                return 1
            fi
        fi
    fi
    return 0
}

# Check for Zenity (for popups)
if ! command -v zenity &>/dev/null; then
    if check_internet; then
        sudo apt install -y zenity
    else
        echo "Zenity not available for popups - using terminal messages"
    fi
fi

# Critical dependencies
install_if_missing python3 python3 true

# Optional dependencies (with internet)
if check_internet; then
    install_if_missing git git
    install_if_missing pip python3-pip
    install_if_missing curl curl

    if ! command -v poetry &>/dev/null; then
        show_popup "Installing Poetry package manager..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi

    # Update project if git repo exists
    if [ -d ".git" ]; then
        if git fetch; then
            LOCAL=$(git rev-parse @)
            REMOTE=$(git rev-parse @{u})
            if [ "$LOCAL" != "$REMOTE" ]; then
                show_popup "Updating project files..."
                git pull
            fi
        fi
    fi

    # Update dependencies
    if command -v poetry &>/dev/null; then
        poetry update || show_popup "Dependency update failed\nUsing existing versions"
    fi
fi

# Launch application
if command -v poetry &>/dev/null; then
    poetry run python youtube_downloader/main.py || \
    show_popup "Launch error" || python3 youtube_downloader/main.py
else
    python3 youtube_downloader/main.py
fi
