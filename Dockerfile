FROM python:3.11-buster AS runner

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD python3 /app/main.py