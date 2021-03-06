FROM python:3.10-slim

WORKDIR /code
COPY . /code/

EXPOSE 6000

RUN pip install -r requirements.txt
CMD ["python","src/bot.py"] 