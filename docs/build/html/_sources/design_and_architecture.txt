Design and Architecture
***********************

Below is a breif explination of how the modules interact with eachother.

Utilities
=========
This is a group of common classes, functions, and parameters that more than one other class use. 
This is where all of the logging functions are defined. :doc:`Documentation for Utilities</Utilities>`.

Populate Database
=================
A set of functions that are used to populate the database with data pulled from the internet
using a statisticsProvider. :doc:`Documentation for Populating Database can be found </scripts.populateDataBase>`.

Wrapper Classes
===============
DataBaseMaintenance is a class that abstracts away many of the functions used to create and 
use connections to the database. It provides an easy way to replace the module used to connect 
to the database. It also uses prepared statements for all calls to the database without exposing
any of the setup or teardown. :doc:`Documentation for the Database Maintenance </wrapper_classes.DbMaintenance>`. 

StatisticsProviders is a group of classes that abstract away code that makes api calls to 
data sources. Currently there is one stats provider that uses two different data sources. 
This module returns a dictionary representation of the JSON object returned from the data source. :doc:`Documentation for the Statistics Providers </wrapper_classes.StatisticsProvider>`.


Ml Classes
==========
A group of classifiers with a common interface. This interface will provide methods for labeling and labeling. :doc:`Documentation for the Classifiers</ml_classes.Classifiers>`.


Feature Extractor provides feature vectors for training and for labeling data. The training method returns a list 
of tuples containing (label, featur vecotr). The labeling method return a list of features that require labeling.  :doc:`Documentation for the FeatureExtractor</ml_classes.FeatureExtractor>`.

