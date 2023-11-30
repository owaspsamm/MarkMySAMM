# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /github/workspace

# Copy the script and the templates directory into the container
COPY requirements.txt /requirements.txt
COPY markmysamm.py /markmysamm.py
COPY templates/ /templates/
RUN ls -la

# Install any needed packages specified in requirements.txt
# You should create a requirements.txt file if you have external dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Run markmysamm.py when the container launches
ENTRYPOINT ["python3", "/markmysamm.py"]
# Temporarily replace the entrypoint for debugging