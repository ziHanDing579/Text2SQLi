# syntax=docker/dockerfile:1

ARG NODE_VERSION=20.10.0
FROM node:${NODE_VERSION}-alpine

# Use production node environment by default
ENV NODE_ENV production

WORKDIR /app

# Expose the port that the application listens on
EXPOSE 3000

COPY package.json ./
RUN npm install
COPY . .
# Run the application
CMD npm start
