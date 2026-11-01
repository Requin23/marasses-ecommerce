FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
ENV NITRO_HOST=0.0.0.0 NITRO_PORT=3000
CMD ["node",".output/server/index.mjs"]
