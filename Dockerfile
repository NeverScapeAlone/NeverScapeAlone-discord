FROM python:3.10-slim

WORKDIR /code
COPY . /code/

EXPOSE 6000

RUN pip install -r requirements.txt
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "6000"] 