# Specify Python version to use for application
FROM python:3.9

# Run commands as user with base privileges
RUN useradd -ms /bin/bash user
USER user

WORKDIR /home/user/SpotifyETL

# Copy requirements to container, install packages, then remove file
ADD requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

# Copy folder containing source files
ADD src/* src/

# Set entry point to the Python script
ENTRYPOINT ["python", "src/main.py"]