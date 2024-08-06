# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install dependencies for glb_to_png
RUN apt-get update && apt-get install -y \
    xvfb \
    libgl1-mesa-glx \
    libglib2.0-0

# Make screenshot_docker.sh executable
RUN chmod +x /app/screenshot_docker.sh

# Run app.py when the container launches
CMD ["python", "app.py"]
