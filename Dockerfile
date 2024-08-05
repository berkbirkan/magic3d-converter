# syntax=docker/dockerfile:1

FROM debian:stretch-slim

# replace shell with bash so we can source files
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# install dependencies
RUN apt-get update \
    && apt-get install -y \
    curl \
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
    wget \
    chromium \
    && apt-get -y autoclean

# nvm environment variables (-> lts/gallium)
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION 16.16.0
RUN mkdir -p ${NVM_DIR}

# install nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash

RUN source ${NVM_DIR}/nvm.sh \
    && nvm install ${NODE_VERSION} \
    && nvm alias default ${NODE_VERSION} \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_BASEDIR ${NVM_DIR}/versions/node/v${NODE_VERSION}
ENV NODE_PATH ${NODE_BASEDIR}/lib/node_modules
ENV PATH ${NODE_BASEDIR}/bin:$PATH

# confirm installation
RUN node -v
RUN npm -v

# install screenshot-glb and puppeteer
RUN npm install -g @shopify/screenshot-glb puppeteer

# specify puppeteer to use the installed Chromium
RUN npx puppeteer install

# setting up the cache directory for puppeteer
ENV PUPPETEER_CACHE_DIR=/app/.cache/puppeteer

# copy the rest of the application to the container
COPY . .

# expose the port that the Flask app will run on
EXPOSE 8889

# define the command to run the application
CMD ["python", "app.py"]
