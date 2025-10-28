# Use Node.js slim image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application code
COPY server.js .
COPY public/ ./public/
COPY data/ ./data/

# Expose port
EXPOSE 3000

# Start the server
CMD ["node", "server.js"]
