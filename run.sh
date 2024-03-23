#!bin/bash

pip install -r requirements.txt

git clone https://github.com/ndrewwang/liiondb.git database/liiondb
cd database/liiondb
git reset --hard ee38d6b
pip install -r requirements.txt
cd ../../

python3 pipeline.py
