FROM python:3.11

WORKDIR /purgador

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . purgador

CMD ["python", "-m", "purgador"]
