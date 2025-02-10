# 使用官方 Python 镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 确保 qr_codes 目录存在
RUN mkdir -p media/qr_codes

# 运行数据库迁移
RUN python manage.py migrate

# 暴露应用运行的端口
EXPOSE 8000

# 启动 Django 开发服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]