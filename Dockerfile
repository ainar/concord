# dev-mode: docker build -t concord . && docker run --rm -it -v $(pwd):/src concord python -m concord
FROM python:3-buster

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
