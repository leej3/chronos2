# Stage-1: Builder
FROM node:20.15.1 AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if present)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the project files
COPY . .

# Build the static files (output will go to 'dist/')
RUN npm run build
ENTRYPOINT ["npm", "run", "dev"]
