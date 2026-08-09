FROM python:3.12-slim

WORKDIR /data

COPY requirements.txt .

# install git
RUN apt-get update
RUN apt-get install -y git

# install python requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]