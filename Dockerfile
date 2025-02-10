# 使用官方 Python 镜像
FROM python:3.9

# 安装 OpenGL 依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 运行 Django 迁移
RUN python manage.py migrate

# 启动 Django 服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]