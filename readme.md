### authorMatcher ###

Author: Pau Perng-Hwa Kung

match authors with corresponding twitter handles

uses ElasticSearch as indexing/database storage

This is a library that semiautomatically builds classification models for matching journalist names with twitter api searched handles, return true if classifier classifies as true. Accuracy ~0.9.

There is also a web app for manual verification between journalist names and handles to build ground truth labels. Using Elasticsearch as backend.

## Packages
need to install and have ElasticSearch running
also need to sign up for Twitter app to obtain respective app keys
other packages- see requirements.txt
