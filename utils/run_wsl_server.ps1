# Uses WSL to run the server as epoll() is Linux-specific
wsl -e bash -c "cd .. && python server.py upload"
