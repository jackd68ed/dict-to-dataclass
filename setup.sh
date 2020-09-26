#!/usr/bin/env bash

python3.8 -m venv venv

venv/bin/pip install --upgrade pip
venv/bin/pip install wheel
venv/bin/pip install -r requirements.dev.txt

pre-commit install
