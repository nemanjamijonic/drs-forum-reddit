# Stage 1: Build the application
FROM node:18.13.0 as build-stage

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the application from Nginx server
FROM nginx:alpine

# Copy the build output to replace the default nginx contents.
COPY --from=build-stage /app/dist/ui /usr/share/nginx/html

# Copy custom nginx configuration
COPY ./nginx-custom.conf /etc/nginx/conf.d/default.conf

# Expose port 8080
EXPOSE 8080

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
