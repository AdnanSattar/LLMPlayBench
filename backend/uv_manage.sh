#!/bin/bash
# Helper script for managing the project with uv

set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Function to display help
show_help() {
    echo "Usage: ./uv_manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install       Install project dependencies"
    echo "  dev           Install development dependencies"
    echo "  run           Run the application"
    echo "  test          Run tests"
    echo "  lock          Update the lock file"
    echo "  help          Show this help message"
    echo ""
}

# Parse command
case "$1" in
    install)
        echo "Installing dependencies..."
        uv pip install -e .
        ;;
    dev)
        echo "Installing development dependencies..."
        uv pip install -e ".[dev]"
        ;;
    run)
        echo "Running application..."
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    test)
        echo "Running tests..."
        uv run pytest "$2"
        ;;
    lock)
        echo "Updating lock file..."
        uv lock
        ;;
    help|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
