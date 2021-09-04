#!usr/bin/sh

dvc run -n clean -d data/abalone.data -d  01_clean_data.py -o data/abalone.csv python 01_clean_data.py
 
dvc run -n summary -d data/abalone.csv -d 02_summary_stats.py python 02_summary_stats.py
