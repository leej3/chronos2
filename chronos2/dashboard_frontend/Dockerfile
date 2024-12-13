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

# Stage-2: Nginx Server
FROM nginx:1.25.2-alpine-slim

# Set permissions for the Nginx HTML directory
RUN chown -R nginx:nginx /usr/share/nginx/html

# Copy the built React files from 'dist/' to Nginx's HTML folder
COPY --from=builder /app/dist /usr/share/nginx/html  

# Change ownership of the files copied from builder
RUN chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
