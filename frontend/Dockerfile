# Multi-stage Dockerfile for Git-Analyzer Frontend

# Stage 1: Build React static bundle
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve with lightweight Caddy
FROM caddy:2-alpine

COPY --from=builder /app/dist /var/www/html
COPY <<EOF /etc/caddy/Caddyfile
:80 {
    root * /var/www/html
    try_files {path} /index.html
    file_server
}
EOF

EXPOSE 80

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
