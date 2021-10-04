FROM python:slim
WORKDIR /app
EXPOSE 5000
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "main.py"]
