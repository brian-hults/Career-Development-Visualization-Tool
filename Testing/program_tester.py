# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 20:34:53 2020

Program Tester

@author: Brian Hults
"""
from clf_driver import CLF_Driver
from bls_qcew_api import BLS_Query
from job_title_matching import Title_Matching
import numpy as np
import time

test_time = time.time()

###############################################################################
'''
# Test the BLS QCEW data pull methods

start_time2 = time.time()
# Get sample data from Fulton County GA
sample_area = '13121'
sample_ind = '1012'

bls = BLS_Query()

# Test out each query function
top_n_emp_data = bls.query_top_emp_jobs(sample_area, top_n=10)
top_n_wage_data = bls.query_top_wage_jobs(sample_area, top_n=10, ind_res=4)
ind_df = bls.query_ind_data(sample_ind, sample_area, ind_res=4, own_type='private')
print('----- Ran BLS API Fetch in {} seconds -----'.format(round(time.time() - start_time2, 2)))

###############################################################################


# Test the Fuzzy String matcher
str_matcher = Title_Matching()

start_time3 = time.time()
# Run Fuzzy String Matcher
fuzz_job_title_list, fuzz_matched_jobs, fuzz_mismatched_jobs = str_matcher.fuzzy_matching()

# Test a user input with two jobs
test_jobs = ['Lab Manager', 'Mechanical Engineer']
user_titles, user_riasec = str_matcher.match_user_input(test_jobs)

# Test user input with a single job and RIASEC scores
test_riasec = [19,25,5,5,6,19] # Quiz scores can be on a scale to a max of 40. The program will scale them down to match the dataset

user_title2, user_riasec2 = str_matcher.match_user_input(test_jobs[0], test_riasec)
print('----- Ran Fuzzy String Matcher in %s seconds -----' % (round(time.time() - start_time3, 2)))

# Test write to file
#str_matcher.write_title_dict(fuzz_job_title_list)

###############################################################################
'''

# Test the CLF Driver program

# Set start time for program timer
start_time1 = time.time()

driver = CLF_Driver(validation=True, drop=True, train_size=0.7)

driver.train_RandomForest()
driver.train_GNB()
driver.train_KNN()

driver.validate_models()

str_matcher = Title_Matching()

# Test a user input with two jobs
test_jobs = ['Lab Manager', 'Mechanical Engineer']
user_titles, user_riasec = str_matcher.match_user_input(test_jobs)

# Test user input with a single job and RIASEC scores
test_riasec = [19,25,5,5,6,19]

user_title2, user_riasec2 = str_matcher.match_user_input(test_jobs[0], test_riasec)

scaled_test_riasec = str_matcher.scale_riasec(test_riasec)
user_ipums_code1 = str_matcher.get_user_ipums_code(user_titles[0])

test_point1 = np.hstack([user_ipums_code1, user_riasec[0], user_riasec[1]])

user_ipums_code2 = str_matcher.get_user_ipums_code(user_title2[0])

test_point2 = np.hstack([user_ipums_code2, user_riasec2, scaled_test_riasec])

driver.test_model(driver.rf_model)
pred1 = driver.predict(driver.rf_model, test_point1, drop=True)
pred2 = driver.predict(driver.rf_model, test_point2, drop=True)
print('----- Ran Driver in {} seconds -----'.format(round(time.time() - start_time1, 2)))

###############################################################################

print('----- Ran Program Tester in {} seconds -----'.format(round(time.time() - test_time, 2)))