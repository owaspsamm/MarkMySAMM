# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /github/workspace

# Copy the script and the templates directory into the container
COPY requirements.txt /github/workspace/
COPY markmysamm.py /github/workspace
COPY templates/ /github/workspace/templates/
RUN ls -la

# Install any needed packages specified in requirements.txt
# You should create a requirements.txt file if you have external dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run markmysamm.py when the container launches
#ENTRYPOINT ["python3", "markmysamm.py"]
# Temporarily replace the entrypoint for debugging
ENTRYPOINT ["sh", "-c", "echo Current directory: $(pwd) && echo Directory contents: $(ls -la) && echo Directory tree: $(tree) && python3 markmysamm.py"]
