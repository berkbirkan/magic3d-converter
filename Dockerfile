# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application to the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 8889

# Define the command to run the application
CMD ["python", "app.py"]
