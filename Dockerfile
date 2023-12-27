FROM python:3.11.7-alpine

RUN pip install mypy
RUN pip install property_based_testing

WORKDIR /srv
