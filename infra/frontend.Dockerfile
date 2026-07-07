FROM node:22-alpine AS build
WORKDIR /app

COPY frontend/bmp-commerce-web/package*.json ./
RUN npm install

COPY frontend/bmp-commerce-web/ ./
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist

EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
