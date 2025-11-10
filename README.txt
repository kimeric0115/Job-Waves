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

The data to be used for the project is currently held in the output folder as final_output.JSON.