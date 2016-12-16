# ensaiNoSQL

# Project Description
The aim of this project is to identify the best place for someone to live in the New York City.
To achieve that, I used data from https://nycopendata.socrata.com. 
My approach to the definition of "best" place  was based on the hypothesis that a "good" borough should have enough health facilities and low air pollution index. In addition there must have sufficient houses, in order for the newcomer to be able to find a plave to live. Finally, I provide some of the most bicycle friendly streets in Manhattan in order for our user to know where it would be easier for him/her to go on bike during his/her daily traverse in the city-center. 
# Datasets Used  
## Based on the requirments the following datasets where used: 
* ## Air quality data collected through a network a sensors 
    More Info: https://data.cityofnewyork.us/Environment/Air-Quality/c3uy-2p5r

* ## Health and Hospitals Corporation (HHC) Facilities 
    This is a list of the 11 acute care hospitals, four skilled nursing facilities, six large diagnostic and treatment centers and community-based clinics that make up the New York City Health and Hospitals Corporation,NYC's public hospital system. HHC is a $6.7 billion integrated healthcare delivery system which serves 1.3 million New Yorkers every year and more than 450,000 are uninsured. It provides medical, mental health and substance abuse services. 
     More Info: https://data.cityofnewyork.us/Health/Health-and-Hospitals-Corporation-HHC-Facilities/f7b6-v6v3

* ## Housing New York Units
    The Department of Housing Preservation and Development (HPD) reports on buildings, units, and projects that began after January 1, 2014 and are counted towards the Housing New York plan. For additional documentation, including a data dictionary.
    More Info: https://data.cityofnewyork.us/Housing-Development/Housing-New-York-Units/sqvz-rbw2

* ## NYCDCP Manhattan Bike Counts - On Street Weekday
    The Transportation Division of the New York City Department of City Planning (NYCDCP) has performed annual bike counts in Manhattan since 1999. The counts have been conducted along designated bicycle routes at 10 on-street and 5 off-street locations during the fall season. These locations have remained generally consistent. The data collected includes cyclist/user volumes, helmet usage, use of bike lane, gender, etc. The bike counts data can offer insights into the overall trends in user demographics and travel patterns over time.
More Info: https://data.cityofnewyork.us/Transportation/NYCDCP-Manhattan-Bike-Counts-On-Street-Weekday/qfs9-xn8t


# Results 
The output is this program is plots showing important information about the datasets, as well as some printed information on the terminal.

# Technical Aspects
 * ## Database Used

     The database I used is MongoDB. It was selected as it is generic NoSQL database that can proccess both fast and in parallel the queries (aggregation/ map-reduce). In addition, it offers Geospatial Indexes that can increase even better the speed of the queries on Geolocation data. This approach wasn't used in the context of this project, mainly due to the lack of corrresponding information in the datasets used.

* ## Required packages

    - urllib (Internal in Python)
    - json (Internal in Python)
    - pymongo (External)
    - matplotlib (External)
    To install the external packages use: `
    ```    
    $ pip install pymongo matplotlib
    ```
# Running the project
To run the project run
```
$ python script.py
```
from the directory where the file is saved.
# ----------------Important--------------------------
To continue the execution of the script after a plot has been displayed, you must first close the window of the figure. 
 

