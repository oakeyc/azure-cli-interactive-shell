FROM azuresdk/azure-cli-python

# WORKDIR azclishell
# COPY . /azclishell

RUN pip install -e .

# WORKDIR /

CMD bash