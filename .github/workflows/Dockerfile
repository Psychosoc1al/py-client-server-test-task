# .github/workflows/Dockerfile
FROM debian:latest

# Install necessary packages
RUN apt update && \
    apt install -y python3-full python3-pip python3-setuptools python3-wheel && \
    apt install -y build-essential && \
    apt install -y git && \
    apt install -y python3-pyqt6 && \
    apt clean

# Set the working directory
WORKDIR /app

# Copy the requirements.txt into the container at /app
COPY requirements.txt /app

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment
RUN source /app/venv/bin/activate

# Install the required packages
RUN pip install -r /app/requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app
