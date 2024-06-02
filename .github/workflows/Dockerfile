# .github/workflows/Dockerfile
FROM debian:latest

# Install necessary packages
RUN apt update && \
    apt install -y python3 python3-pip python3-setuptools python3-wheel && \
    apt install -y build-essential && \
    apt install -y git && \
    apt install -y python3-pyqt6 && \
    apt clean

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install PyInstaller
RUN pip install -r requirements.txt
