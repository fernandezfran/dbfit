#!bin/bash

git clone https://github.com/ndrewwang/liiondb.git database/liiondb

pip install -r database/liiondb/requirements.txt

python3 main.py
