@echo off
REM Minima MCP Server Launcher
REM This script sets up the environment and starts the MCP server

REM Set environment variables
set MINIMA_HOST=127.0.0.1
set MINIMA_PORT=9003
set MINIMA_MDS_PASSWORD=cc1155CCcc1155CC!

REM Add src to Python path
set PYTHONPATH=%~dp0src

REM Start the server
cd /d %~dp0
python -m minima_mcp.server
