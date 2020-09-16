# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 16:20:22 2020

CSE 6242 - ONET Job Title to RAISEC Scores Processing

@author: Brian Hults
"""
# Import packages
import pandas as pd
from collections import defaultdict
import time

start_time = time.time()

# Get the occupation and interest data
onet_occupation_data = pd.read_csv('Occupation Data.txt', header=0, sep='\t', usecols=['O*NET-SOC Code', 'Title'])
onet_interest_data = pd.read_csv('Interests.txt', header=0, sep='\t', usecols=['O*NET-SOC Code', 'Element Name', 'Scale ID', 'Data Value'])

# Filter out the Interest High-Point Scale data since we are only using RAISEC Scores
onet_interest_data = onet_interest_data[onet_interest_data['Scale ID'] != 'IH']

# Merge the two dataframes to get Occupation title and RAISEC scores in the same df
onet_jobs_interests = onet_occupation_data.merge(onet_interest_data, how='inner', on='O*NET-SOC Code')

# Convert the dataframe to a dictionary for easier use access
onet_job_interest_dict = defaultdict()

# Combine the set of scores for each job title into a single dictionary for that job key
# Source: https://datascience.stackexchange.com/questions/32328/export-pandas-to-dictionary-by-combining-multiple-row-values
for i in onet_jobs_interests['Title'].unique():
    onet_job_interest_dict[i] = [onet_jobs_interests['Data Value'][j] for j in onet_jobs_interests[onet_jobs_interests['Title']==i].index]

# Convert dictionary to Dataframe and write to text file
out_df1 = pd.DataFrame.from_dict(onet_job_interest_dict, orient='index').reset_index()
out_df1.columns = ['ONET Title','R','I','A','S','E','C']
out_df1.dropna(axis=0, how='any', inplace=True)

# Load the IPUMS title data to create an IPUMS title to RIASEC code table
ipums_job_titles = pd.read_csv('ipums_job_title_codes_2010_basis.txt', sep='\t', dtype=str, na_values=['Unknown'])
ipums_job_titles.dropna(axis=0, how='any', inplace=True)
ipums_job_titles['Title'] = ipums_job_titles['Title'].str.replace(', nec', '')
ipums_to_onet_titles = pd.read_csv('job_title_matching_dictionary.txt', sep='\t', dtype=str, header=0)

out_df2 = pd.merge(ipums_to_onet_titles, out_df1, on='ONET Title', how='inner')
out_df3 = pd.merge(ipums_job_titles, out_df2, left_on='Title', right_on='IPUMS Title', how='inner')
out_df3.drop('Title', axis=1, inplace=True)
out_df3.rename(columns={'Code': 'IPUMS Code'}, inplace=True)

out_df1.to_csv('onet_job_to_riasec_scores.txt', sep='\t', header=out_df1.columns, index=False, mode='w')
out_df3.to_csv('onet_ipums_job_to_riasec_scores.txt', sep='\t', header=out_df3.columns, index=False, mode='w')

print('----- Created Job Title to Score Dictionary in %s seconds -----' % (round(time.time() - start_time, 2)))
