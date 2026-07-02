# build stage
FROM node:20-alpine AS build
WORKDIR /app
ARG VITE_API_BASE_URL=
ARG VITE_API_KEY=read-dev-key
ARG VITE_API_KEY_WRITE=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_API_KEY=${VITE_API_KEY}
ENV VITE_API_KEY_WRITE=${VITE_API_KEY_WRITE}
COPY package*.json ./
# Prefer reproducible installs; fall back if lockfile missing
RUN npm ci || npm install
COPY . .
RUN npm run build

# run stage
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
