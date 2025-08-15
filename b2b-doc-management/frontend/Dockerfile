FROM node:22

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY . .

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Angular application
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN npm run build --prod

# Expose the port the app runs on
EXPOSE 4200

# Command to run the application
CMD ["npm", "start"]