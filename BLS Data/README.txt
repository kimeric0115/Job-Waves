# Employment & Unemployment (CE): Average Hourly Earnings of All Employees, In Dollars
# Job Openings and Labor Turnover Survey (JT): All employees, in thousands
# State and Area Employment, Hours, and Earnings (SMU): measuring the number of job openings in a given period of time

The order of the code goes from parsing_industry_inputs.py --> getting_data.py --> organization.py.

parsing_industry_inputs:
This just parses through the txt inputs of all the possible industry labels and takes the industries listed as display_level 2 (there should be around 11-12), and then turns it into a JSON file that contains series_id and administrative columns organizing the data.

getting_data:
Using the newly created JSON files as a guideline, I use them to get all the industries that are display_level 2 and then using that list, I input those industries into the API using the series_ids, then output to the output folder as "{data set}_data". Alongside those JSON files, I also created a dictionary to keep track of the names of the industries relative to their (what I call) codes, or the id that we input into the API to be used later in creating our own dataframe.

organization:
This organizes all the datasets and joins the three. I organize by getting rid of the series_id and inputting the new "name" column for joining. I also noticed that the JT dataset split the "government" industry into "local and state" and "federal" or something along those lines, so I grouped and aggregated their values into one row (from two) so that joining would be 1-to-1. I then joined (merged) the three data frames and then transferred it into a JSON file, final_output.JSON.

data_merge:
After taking the BLS data from the API, it was merged with other hypotheses that looked at Reddit API data as well, resulting in another intermediary file in the output folder called "merged_data.json".

clean_data:
Finally, "merged_data.json" was cleaned and thus led to the actual final data file to be labeled, "cleaned_data.json" file. Our final resulting JSON file is structured primarily by industry name, and there are multiple columns that list the month/year's statistics and influential reddit post that we scraped via an API. To delve into our fields, we have 7 influential fields worth documenting:

"sector": the industry/sector that includes construction, information, education, etc. such that these names are overarching umbrellas terms for wide arrays of jobs. This field is required and should not be null. We have 10 possible values for industries, contained in: ['mining and logging', 'construction', 'manufacturing', 'trade, transportation, and utilities', 'information', 'financial activities', 'professional and business services', 'private education and health services', 'leisure and hospitality', 'government']. 

"year"/"Month": self-explanatory; we organize our data based on time-frame of the year. These fields are required, and cannot be null. This value is not technically unique considering that we observe the same time frames across 10 different industries.