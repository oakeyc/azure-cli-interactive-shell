#! /usr/bin/bash

rm -rf -y dist/*
python setup.py sdist
twine upload dist/*

docker build --no-cache -t oakeyc/az-cli-shell .
docker push oakeyc/az-cli-shell
