# Uses WSL to run the server as epoll() is Linux-specific
wsl -e bash -c "cd .. && source .venv/debian-venv/bin/activate && python src/server.py upload"
