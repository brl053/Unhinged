# Use Node.js as the base image for building
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files first for caching
COPY package.json ./
COPY package-lock.json* ./
# Use 'npm install' since package-lock.json might not exist
RUN npm install

# Copy the rest of the frontend code
COPY . ./

# Build the React app
RUN npm run build

# Use Nginx for serving the frontend
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy the built React app from the build stage
# Updated from /app/build to /app/dist
COPY --from=build /app/dist .

# Expose the web server port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
