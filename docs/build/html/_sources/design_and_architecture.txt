Design and Architecture
***********************

Utilities
=========
This is a group of common classes, functions, and parameters that more than
one other class uses. This is where all of the logging functions are defined.
:doc:`Documentation for Utilities</Utilities>`.

Populate Database
=================
A set of functions that are used to populate the database with data pulled
from the internet using a statisticsProvider object.
:doc:`Documentation for Populating Database </scripts.populateDataBase>`.

Wrapper Classes
===============
DataBaseMaintenance is a class that abstracts away many of the functions used
to create and use connections to the database. It provides an easy way to
replace the module used to connect to the database. It also uses prepared
statements for all calls to the database without exposing any of the setup or
teardown.
:doc:`Documentation for the Database Maintenance </wrapper_classes.DbMaintenance>`.

StatisticsProvider is a group of classes that abstract away code that makes
api calls to data sources. Currently there is one stats provider that uses
two different data sources. This module returns a dictionary representation
of the JSON object returned from the data source.
:doc:`Documentation for the Statistics Providers </wrapper_classes.StatisticsProvider>`.


Ml Classes
==========
Classifiers is a group of classifiers with a common interface. This interface
will provide methods for training and labeling.
:doc:`Documentation for the Classifiers</ml_classes.Classifiers>`.


Feature_Extractor provides feature vectors for training and for labeling data.
The training method returns a list of tuples containing (label, feature
vector). The labeling method return a list of features that require labeling.
:doc:`Documentation for the FeatureExtractor</ml_classes.FeatureExtractor>`.

