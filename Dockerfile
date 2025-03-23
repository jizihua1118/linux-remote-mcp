FROM python:3.8-slim

WORKDIR /app

# 复制项目文件
COPY mcp_service.py .
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置可执行权限
RUN chmod +x mcp_service.py

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 启动命令（将由smithery.yaml中定义的命令替代）
CMD ["python", "mcp_service.py", "--help"] 