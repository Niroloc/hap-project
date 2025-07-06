FROM python:3.10.12

COPY requirements.txt /app/build/requirements.txt
WORKDIR /app/build/
RUN pip3 install -r requirements.txt
ADD src /app/src
WORKDIR /app/src

CMD ["python3", "-u", "main.py"]