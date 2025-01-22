#!/bin/bash
export PYTHONPATH=$(pwd)
pytest pytest/test_prompt.py -s
