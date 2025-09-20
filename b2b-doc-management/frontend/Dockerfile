# Use official Node image to run Angular dev server
FROM node:22-alpine

# Install Git
RUN apk add --no-cache git

# Create app directory
WORKDIR /app
# Copy package files first to take advantage of Docker cache
COPY . .


# Install Angular CLI globally so `ng` is available, then install deps for the app
RUN npm install -g @angular/cli@latest



# Configure Git user email and name
RUN git config --global user.email "kent7493@icloud.com" && \
    git config --global user.name "yichia"

# Expose Angular dev server port
EXPOSE 4200

# Start dev server and listen on all interfaces so it is reachable from host
CMD ["ng", "serve", "--host", "0.0.0.0"]

