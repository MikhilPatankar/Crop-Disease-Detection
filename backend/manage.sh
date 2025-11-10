#!/bin/bash
set -e

#
# Management script for the Crop Disease Detection backend.
#
# This script provides commands to initialize the project, manage database
# migrations, and run the development server. It is designed to work on
# both Linux/macOS and Windows (with Git Bash, WSL, or Cygwin).
#

VENV_DIR="env"
BACKEND_DIR="backend"
APP_MODULE="backend.main:app"
HOST="127.0.0.1"
PORT="5000"

VENV_PYTHON="python"
ALEMBIC_EXEC="alembic"
UVICORN_EXEC="uvicorn"

if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
    ALEMBIC_EXEC="$VENV_DIR/bin/alembic"
    UVICORN_EXEC="$VENV_DIR/bin/uvicorn"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
    ALEMBIC_EXEC="$VENV_DIR/Scripts/alembic.exe"
    UVICORN_EXEC="$VENV_DIR/Scripts/uvicorn.exe"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Virtual environment not found at '$VENV_DIR'."
    echo "Please create it first by running: python -m venv $VENV_DIR"
    exit 1
fi


function install_deps() {
    echo "Installing/updating dependencies from requirements.txt..."
    if [ -f "requirements.txt" ]; then
        "$VENV_PYTHON" -m pip install -r requirements.txt
        echo "Dependencies installed successfully."
    else
        echo "Warning: requirements.txt not found. Skipping dependency installation."
        echo "Please create a requirements.txt file with your project's dependencies."
    fi
}

function run_migrations() {
    echo "Running database migrations..."
    (cd "$BACKEND_DIR" && "$ALEMBIC_EXEC" upgrade head)
    echo "Migrations applied successfully."
}

function make_migrations() {
    if [ -z "$1" ]; then
        echo "Error: Migration message is required."
        echo "Usage: ./manage.sh makemigrations \"Your migration message\""
        exit 1
    fi
    echo "Creating new migration: $1"
    (cd "$BACKEND_DIR" && "$ALEMBIC_EXEC" revision --autogenerate -m "$1")
    echo "New migration created."
}

function run_server() {
    echo "Starting backend server at http://$HOST:$PORT..."
    "$UVICORN_EXEC" "$APP_MODULE" --host "$HOST" --port "$PORT" --reload --reload-dir "$BACKEND_DIR"
}

function show_help() {
    echo "Usage: ./manage.sh {init|install|migrate|makemigrations|runserver|help}"
    echo
    echo "Commands:"
    echo "  init             - Runs 'install' and 'migrate'. Use for first-time setup."
    echo "  install          - Install/update dependencies from requirements.txt."
    echo "  migrate          - Apply database migrations to the latest version."
    echo "  makemigrations   - Create a new database migration file."
    echo "                     Requires a message in quotes, e.g., ./manage.sh makemigrations \"create users table\""
    echo "  runserver        - Start the FastAPI development server."
    echo "  help             - Show this help message."
}

COMMAND=$1

if [ -z "$COMMAND" ]; then
    show_help
    exit 0
fi

case "$COMMAND" in
    init) install_deps && run_migrations ;;
    install) install_deps ;;
    migrate) run_migrations ;;
    makemigrations) shift; make_migrations "$@" ;;
    runserver) run_server ;;
    help|*) show_help ;;
esac

