# Use official Node.js image for Angular
FROM node:22-alpine

# 設定工作目錄
WORKDIR /app

# 複製 package.json 及 package-lock.json
COPY package.json ./
# COPY package-lock.json ./

# 安裝 npm 依賴
RUN npm install
RUN npm install -g @angular/cli

# 複製所有專案檔案
COPY . .

# 開放 4200 port
EXPOSE 4200

# 啟動 Angular 開發伺服器
CMD ["npm", "start"]
