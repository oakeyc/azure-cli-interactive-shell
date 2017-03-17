FROM python:3.6

WORKDIR azclishell
COPY . /azclishell

# RUN pip install --update

WORKDIR /

CMD bash