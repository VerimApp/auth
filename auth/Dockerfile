FROM python:3.11.5-slim

ENV DEFAULT_SERVICE_DIR /microservice

RUN mkdir $DEFAULT_SERVICE_DIR

COPY ./auth/ $DEFAULT_SERVICE_DIR
COPY ./protobufs/ /protobufs/
COPY ./.vscode/ $DEFAULT_SERVICE_DIR/.vscode/

WORKDIR $DEFAULT_SERVICE_DIR

RUN pip install pip==21.3.1
RUN pip install poetry
RUN poetry export --without-hashes -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

CMD ["./boot.sh"]
