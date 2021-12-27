FROM node:16-bullseye

WORKDIR /usr/src/bridgeapp

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build
