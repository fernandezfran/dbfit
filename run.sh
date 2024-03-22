#!bin/bash

git clone https://github.com/ndrewwang/liiondb.git database/liiondb

pip install -r requirements.txt

python3 train.py
