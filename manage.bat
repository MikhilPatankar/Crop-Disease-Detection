@echo off
setlocal

::
:: Management script for the Crop Disease Detection backend (Windows version).
::
:: This script provides commands to initialize the project, manage database
:: migrations, and run the development server.
::

:: --- Configuration ---
set "VENV_DIR=env"
set "BACKEND_DIR=backend"
set "APP_MODULE=backend.main:app"
set "HOST=0.0.0.0"
set "PORT=5000"
set "HOST_LINK=127.0.0.1"

:: --- Main Logic ---
set "COMMAND=%~1"

if "%COMMAND%"=="" goto :show_help
if /I "%COMMAND%"=="init" goto :init
if /I "%COMMAND%"=="install" goto :install_deps
if /I "%COMMAND%"=="migrate" goto :run_migrations
if /I "%COMMAND%"=="makemigrations" goto :make_migrations
if /I "%COMMAND%"=="runserver" goto :run_server
if /I "%COMMAND%"=="help" goto :show_help

echo Unknown command: %COMMAND%
goto :show_help

:: --- Command Functions ---

:init
    echo Running initialization...
    call :install_deps
    call :run_migrations
    echo Initialization complete.
    goto :eof

:install_deps
    echo Installing/updating dependencies from requirements.txt...
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt
        echo Dependencies installed successfully.
    ) else (
        echo Warning: requirements.txt not found. Skipping dependency installation.
    )
    goto :eof

:run_migrations
    echo Running database migrations...
    pushd "%BACKEND_DIR%"
    "%ALEMBIC_EXEC%" upgrade head
    popd
    echo Migrations applied successfully.
    goto :eof

:make_migrations
    shift
    set "MESSAGE=%*"
    if not defined MESSAGE (
        echo Error: Migration message is required.
        echo Usage: manage.bat makemigrations "Your migration message"
        goto :eof
    )
    echo Creating new migration: %MESSAGE%
    pushd "%BACKEND_DIR%"
    "%ALEMBIC_EXEC%" revision --autogenerate -m "%MESSAGE%"
    popd
    echo New migration created.
    goto :eof

:run_server
    echo Starting backend server at http://%HOST_LINK%:%PORT%...
    uvicorn %APP_MODULE% --host %HOST% --port %PORT% --reload --reload-dir "%BACKEND_DIR%"
    goto :eof

:show_help
    echo Usage: manage.bat {init^|install^|migrate^|makemigrations^|runserver^|help}
    echo.
    echo Commands:
    echo   init             - Runs 'install' and 'migrate'. Use for first-time setup.
    echo   install          - Install/update dependencies from requirements.txt.
    echo   migrate          - Apply database migrations to the latest version.
    echo   makemigrations   - Create a new database migration file.
    echo                      Requires a message in quotes, e.g., manage.bat makemigrations "create users table"
    echo   runserver        - Start the FastAPI development server.
    echo   help             - Show this help message.
    goto :eof

