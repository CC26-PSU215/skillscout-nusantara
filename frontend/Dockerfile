FROM node:20-alpine

WORKDIR /app

# Copy package lists
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Start the Next.js development server
CMD ["npm", "run", "dev"]