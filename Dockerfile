FROM python:2.7.14-alpine

WORKDIR /app
COPY . /app

EXPOSE 5000

RUN pip install -r requirements.txt
RUN --mount=type=secret,id=API_POGODA \
  --mount=type=secret,id=BD_HOST \
  --mount=type=secret,id=BD_PASS \
  export API_POGODA=$(cat /run/secrets/API_POGODA) && \
  export BD_HOST=$(cat /run/secrets/BD_HOST) && \
  export BD_PASS=$(cat /run/secrets/BD_PASS)
CMD FLASK_APP=api.py flask run --host="::"