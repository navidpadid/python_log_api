FROM python:3.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
COPY log_generator.py ./
RUN python log_generator.py
RUN mv log1.log /var/log
RUN mv log2.log /var/log
CMD ["python", "app.py"]
