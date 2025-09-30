# 使用官方 Nginx 映像
FROM nginx:latest

# 複製自定義 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 複製你的網頁檔案到 Nginx 預設的網頁目錄
COPY b2c-doc-management/dist/b2c-doc-management/browser /usr/share/nginx/html

# 暴露 80 和 443 端口
EXPOSE 80
EXPOSE 443

# 啟動 Nginx
CMD ["nginx", "-g", "daemon off;"]