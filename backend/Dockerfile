FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt --no-cache-dir
COPY entrypoint.sh /app/entrypoint.sh

COPY . .

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi:application"]