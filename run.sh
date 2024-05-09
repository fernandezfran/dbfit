#!bin/bash

# install the required versions of galpynostatic, scipy and scikit-learn
pip install -r requirements.txt

# clone the LiionDB from github, go to the last tested commit, and install
# its requirements
git clone https://github.com/ndrewwang/liiondb.git api/database/liiondb
cd api/database/liiondb
git reset --hard ee38d6b
pip install -r requirements.txt

# go back to api dir and create the res folder to save the results
cd ../../
mkdir res/

# run the pipeline in the api folder
python3 pipeline.py

# get the plots
python3 plot.py

# mv res/ to the main folder
cd ../
mv api/res/ .
