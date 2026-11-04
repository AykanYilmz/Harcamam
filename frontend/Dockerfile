# Two images from one file:
#   --target dev   Vite dev server; docker-compose.yml bind-mounts the source
#   --target prod  (default) the built site served by nginx, which also proxies /api

FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci


FROM deps AS dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]


FROM deps AS build
COPY . .
# Same origin as the site: nginx forwards /api to the backend, so no CORS is needed.
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build


FROM nginx:1.27-alpine AS prod
# The official image fills these into templates/*.template at startup. 127.0.0.11 is
# Docker's internal DNS; on other platforms set DNS_RESOLVER to theirs.
ENV BACKEND_URL=http://backend:8000 \
    DNS_RESOLVER=127.0.0.11
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s CMD wget -q --spider http://127.0.0.1/healthz || exit 1
