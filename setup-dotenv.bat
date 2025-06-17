@echo off
setlocal enabledelayedexpansion

REM Copy all .env.sample files to .env.docker
for /r %%f in (*.env.sample) do (
    set "src=%%f"
    set "dest=%%f"
    set "dest=!dest:.sample=.docker!"
    copy "!src!" "!dest!" >nul
    echo Copied !src! to !dest!
)

REM Copy all .env.sample.local files to .env
for /r %%f in (*.env.sample.local) do (
    set "src=%%f"
    set "dest=%%f"
    set "dest=!dest:.sample.local=!"
    copy "!src!" "!dest!" >nul
    echo Copied !src! to !dest!
)

endlocal

docker compose up --build
