#!/bin/bash

# Run tests with coverage
pytest bot/tests/ --cov=bot --cov-report=term-missing -v