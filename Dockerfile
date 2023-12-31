FROM python:3.11.7-alpine

RUN pip install mypy
RUN pip install property_based_testing==0.0.5

WORKDIR /srv
