FROM node:14-buster

WORKDIR /usr/src/bridgeapp

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build
