# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Create a new Angular app
RUN ng new b2b-doc-management-frontend --directory . --routing --style css --skip-git --defaults

# Copy the rest of the application's source code from the host to the image's filesystem.
COPY . .

# Expose port 4200 to the outside world
EXPOSE 4200

# Command to run the app
CMD ["ng", "serve", "--host", "0.0.0.0"]
