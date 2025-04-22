#!/bin/bash

set -e  # Exit on any error

# Helper to install a package if missing
install_if_missing() {
    local cmd=$1
    local pkg=$2

    if ! command -v "$cmd" &>/dev/null; then
        echo "🔧 '$cmd' not found. Installing '$pkg'..."
        sudo apt update
        sudo apt install -y "$pkg"
    else
        echo "✅ '$cmd' is already installed."
    fi
}

echo "🔍 Checking and installing prerequisites..."

install_if_missing git git
install_if_missing python3 python3
install_if_missing pip pip
install_if_missing curl curl

if ! command -v poetry &>/dev/null; then
    echo "🔧 'poetry' not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    # Add Poetry to PATH immediately
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ All dependencies are ready."

echo "🔄 Checking for updates in git repo..."
git fetch
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⬆️  Updating project from remote..."
    git pull
else
    echo "✅ Project is already up-to-date."
fi

echo "📦 Ensuring dependencies are up-to-date..."
poetry update

echo "🚀 Launching downloader..."
poetry run python youtube_downloader/main.py
