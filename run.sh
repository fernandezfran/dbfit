#!bin/bash

pip install -r requirements.txt

git clone https://github.com/ndrewwang/liiondb.git api/database/liiondb
cd api/database/liiondb
git reset --hard ee38d6b
pip install -r requirements.txt
cd ../../

python3 pipeline.py
