NFL Fantasy Football Stats Aggregation and analysis package

Description
-----------
  This project is a set of scripts and modules meant to aid in setting a fantasy football lineup. This package coupled with a Django web app uses API calls to download player stats, game information, and weather information. This data is then inserted into a MySQL database. Currently, a set of machine learning modules is being developed to rank players based on game location, previous performance, opponent, etc. 
  
Install
-------
  There are two runnable python scripts in this project. One is a script to populate an empty database and the other is script to do some very basic machine learning (currently under development). 
  
Linux:
  In order to run these scripts, ./src must be in your python path. 
  
  To achieve this, clone this repo in your home folder. Then add the absolute path to your python path by adding the following line to your .profile:
  
  `export PYTHONPATH=$HOME/nflStatsProj/src`
  
  Finally, you need to add a config.yaml file to `nflStats/Proj/config` to point to your database. 
  
  Ex. 
  db:
    ip: localhost
     username: username
     password: password
     database: database


Documentation
-------------
  All documentation is generated using Sphinx.
  
  If you would like to generate documentation `cd` into docs and `type make html`. This builds all of the html files and drops
them in `./build/html`.
  
Bug Report/Contact
------------------
  To report a bug or to contact me please email me at: derrick2105@gmail.com
Please add nflStatsProj to the subject line.

LinkedIn Profile:
  https://www.linkedin.com/in/derrick-smith-91501463

