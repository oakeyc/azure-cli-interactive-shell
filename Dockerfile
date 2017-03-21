FROM azuresdk/azure-cli-python

WORKDIR . /.
COPY . .

RUN pip install -e .

WORKDIR /

# CMD bash