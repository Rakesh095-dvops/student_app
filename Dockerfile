# Dockerfile
FROM python:3.13-slim
    
WORKDIR /app
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
    
COPY . .
EXPOSE 5000
#HEALTHCHECK --interval=30s --timeout=5s --retries=3   CMD wget -q -O - http://localhost:5000/health || exit 1
# Use a lightweight web server for production    
CMD ["python", "app.py"]