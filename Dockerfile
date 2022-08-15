FROM python:3.10-slim

WORKDIR /code
COPY . /code/

EXPOSE 6000

RUN pip install -r requirements.txt
CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0"]