FROM python:3.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY random_logs/log1.log /var/log/log1.log
COPY random_logs/log2.log /var/log/log2.log
EXPOSE 5000
CMD ["python", "app.py"]
