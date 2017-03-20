FROM oakeyc/az-cli-shell

WORKDIR azclishell
COPY . /azclishell

RUN pip install azure-cli-shell

# RUN az-shell

WORKDIR /

CMD bash