# Note LF EOL to use multiline commands

# Uses WSL with Debian 12 installed to build binaries
wsl -e bash -c "
source ../.venv/debian-venv/bin/activate &&
python -m PyInstaller \
    --clean \
    --onefile \
    --add-data=../.env:. \
    --specpath=../build \
    --workpath=../build \
    --distpath=../Debian-12-dist \
    ../src/client.py
"

Write-Output `n`n

wsl -e bash -c "
source ../.venv/debian-venv/bin/activate &&
python -m PyInstaller \
    --clean \
    --onefile \
    --add-data=../.env:. \
    --specpath=../build \
    --workpath=../build \
    --distpath=../Debian-12-dist \
    ../src/server.py
"
