# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for screenshot-glb
RUN apt-get update && apt-get install -y \
    sudo \
    wget \
    gconf-service \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libnss3 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Set environment variable to skip downloading Chromium
ENV PUPPETEER_SKIP_DOWNLOAD=true

# Install screenshot-glb
RUN npm install -g @shopify/screenshot-glb

# Copy the requirements.txt file to the container
COPY requirements.txt requirements.txt

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application to the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 8889

# Define the command to run the application
CMD ["python", "app.py"]
