Intro
*****

What is this?
=============
This project is a collection of modules and scripts meant to help set a fantasy
football lineup. Included is a script to populate a database, a script to
rank players based on past performance using supervised machine learning, and
a set of wrapper modules to abstract away the details of the backing database.

Why did I create this? 
======================
I like to play fantasy football, but the amount of time required to set a
lineup makes playing competitively every year unrealistic. I set out to be
competitive by aggregating player stats into a local database that is easily
queried. A sample query involve selecting the average points an opposing
defense has allowed wide receivers. Prior to aggregating these stats, the
above query would on average involve visiting 2-3 different websites per
potential player. Now, it is a matter of building a single query that takes
as input a list of possible receivers. This aggregation has lead to a 25%
increase in my average wins per season over the last 2 seasons.

Also, this project will increase my win percentage even more by allowing
me to use supervised machine learning to influence the players I draft. Since
some players are more reliable from season to season, the player ranking feature
will help tease out the players who tend to perform better on average.

Goals
=====
The main goal of this project is to reduce the time spent setting a fantasy
football lineup while remaining competitive. I have already achieved a
roughly 25% increase in total wins per season while reducing the amount of
time I spend setting a lineup by more than 50%.

Use supervised machine learning to rank players in each position based on past
performance and current weather conditions. However, I currently do not have
enough weather information to include weather in the feature vectors used to
predict weekly and season performance.

Fully automate weekly stats updates by creating a daemonized python script.
Since the current script has all of the methods needed to automate
this, it is just a matter of removing the class from the script and running
the script once a week.

I am currently using the data in the database to build a Django web app to
make the results of the queries more human readable in order to reduce the
total time I spend setting a lineup by another 25-50%.

Finally, a side goal of this project is to continually refine my python
skills by periodically reviewing my design decisions. This review will help me
improve code readability and improve performance by optimizing each section
of the code.