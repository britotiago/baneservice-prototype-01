# Dockerfile for Frontend
FROM node:18 AS builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Copy environment variables
COPY .env.production.local ./

# Build the Next.js application
RUN npm run build

# Use a smaller, more optimized image for production
FROM node:18-slim AS production
WORKDIR /app

# Copy the Next.js build and dependencies from the build stage
COPY --from=builder /app/ ./

# Expose the Next.js default port
EXPOSE 3000

# Start Next.js in production mode
CMD ["npm", "run", "start"]
