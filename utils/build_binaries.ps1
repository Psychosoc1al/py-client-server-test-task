# Note LF EOL to use multiline commands

# Uses WSL with Debian 12 installed to build binaries
wsl -e bash -c "
source ../.venv/debian-venv/bin/activate &&
pyinstaller \
    --clean \
    --onefile \
    --add-data=../.env:. \
    --icon=../icons/server.ico \
    --specpath=../build \
    --workpath=../build \
    --distpath=../Debian-12-dist \
    ../src/server.py && \
echo $'\n\n' && \
pyinstaller \
    --clean \
    --onefile \
    --add-data=../.env:. \
    --add-data=../icons/client.ico:icons \
    --icon=../icons/client.ico \
    --specpath=../build \
    --workpath=../build \
    --distpath=../Debian-12-dist \
    ../src/client.py
"
