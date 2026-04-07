FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json tsconfig.json tsconfig.app.json vite.config.ts index.html /app/
COPY src /app/src

RUN npm ci
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
