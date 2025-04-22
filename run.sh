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

# Check internet connection first
if check_internet; then

    # Ensure git is installed before repo update
    install_if_missing git git true

    # Check for repo updates as top priority
    if [ -d ".git" ]; then
        git fetch || show_critical_error "Failed to fetch repo updates."
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse @{u})

        if [ "$LOCAL" != "$REMOTE" ]; then
            CHANGED_FILES=$(git diff --name-only "$LOCAL" "$REMOTE")
            git pull || show_critical_error "Failed to pull updates from remote."

            if echo "$CHANGED_FILES" | grep -q "$(basename "$0")"; then
                echo "🔁 Script was updated. Restarting..."
                exec "$0" "$@"
            fi
        fi
    fi

    # Optional dependencies
    install_if_missing pip python3-pip false
    install_if_missing curl curl false

    if ! command -v poetry &>/dev/null; then
        curl -sSL https://install.python-poetry.org | python3 - || true
        export PATH="$HOME/.local/bin:$PATH"
    fi

    # Install project dependencies first
    if command -v poetry &>/dev/null; then
        poetry install || show_critical_error "Dependency installation failed via Poetry."

        # Then optionally update them
        poetry update || echo "⚠️ Poetry update failed. Continuing with existing versions."
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
