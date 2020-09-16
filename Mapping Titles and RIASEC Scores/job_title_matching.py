# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 20:39:43 2020

CSE 6242 - Job Code-Title Data Processing

@author: Brian Hults
"""

# Import packages
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz


class Title_Matching:
    def __init__(self, threshold=0.9, ipums_title_codes_path=None, occ_data_path=None, \
                 alt_titles_path=None, match_dict_path=None, riasec_scores_path=None , ind_titles_path=None):

        if ipums_title_codes_path is None:
            self.ipums_title_codes_path = 'ipums_job_title_codes_2010_basis.txt'
        else:
            self.ipums_title_codes_path = ipums_title_codes_path

        if occ_data_path is None:
            self.occ_data_path = 'Occupation Data.txt'
        else:
            self.occ_data_path = occ_data_path

        if alt_titles_path is None:
            self.alt_titles_path = 'Alternate Titles.txt'
        else:
            self.alt_titles_path = alt_titles_path

        if match_dict_path is None:
            self.match_dict_path = 'job_title_matching_dictionary.txt'
        else:
            self.match_dict_path = match_dict_path

        if riasec_scores_path is None:
            self.riasec_scores_path = 'onet_job_to_riasec_scores.txt'
        else:
            self.riasec_scores_path = riasec_scores_path

        if ind_titles_path is None:
            self.ind_titles_path = 'industry_titles.csv'
        else:
            self.ind_titles_path = riasec_scores_path

        data = self.read_data()
        self.ipums_titles = data[0]
        self.onet_titles = data[1]
        self.onet_alt_titles = data[2]
        self.titles_riasec_scores = data[3]
        self.ipums_code_titles = data[4]
        self.ind_titles = data[5]
        self.fuzzy_threshold = 0.9
        self.file_check()


    '''
    file_check - function to check if there is an exisitng job title dictionary.
    If so, import it and only append to it.
    '''
    def file_check(self):
        try:
            saved_df = pd.read_csv(self.match_dict_path, header=0, index_col=0, sep='\t')
            job_arr = saved_df.to_numpy()
            self.job_list = job_arr.tolist()
            self.access_mode = 'r'

        # If there is no existing dictionary, set access mode to full write access to create a new file.
        except:
            self.job_list = None
            self.access_mode = 'w'


    '''
    read_data - function that
    '''
    def read_data(self):
        # Set list of titles to consider as NA and drop
        na_list = ['Unknown']

        # Read in job title code data
        ipums_job_title_code_2010_basis = pd.read_csv(self.ipums_title_codes_path, \
                                                      sep='\t', header=0, dtype=str, \
                                                      na_values=na_list)

        # Get rid of items matching titles in the NA list
        ipums_job_title_code_2010_basis.dropna(axis=0, how='any', inplace=True)

        # Read in ONET Job title and description data
        onet_occupation_data = pd.read_csv(self.occ_data_path, sep='\t', header=0)

        # Read in ONET Alternate Job title samples
        onet_alt_job_titles = pd.read_csv(self.alt_titles_path, sep='\t', header=0, usecols = [0,1])
        onet_alt_job_titles = onet_occupation_data.merge(onet_alt_job_titles, how='inner', on='O*NET-SOC Code')
        onet_alt_job_titles.drop(columns=['O*NET-SOC Code', 'Description'], inplace=True)

        # Extract ONET and IPUMS job titles
        onet_job_titles = onet_occupation_data['Title']
        ipums_job_titles = ipums_job_title_code_2010_basis['Title']
        ipums_job_titles = ipums_job_titles.str.replace(', nec', '')

        # Read in the Titles to RIASEC scores map produced by the onet_ipums_title_to_riasec.py program
        titles_riasec_scores = pd.read_csv(self.riasec_scores_path, sep='\t', header=0)

        ind_titles = pd.read_csv(self.ind_titles_path, sep=',', header=0)

        return ipums_job_titles, onet_job_titles, onet_alt_job_titles, titles_riasec_scores, ipums_job_title_code_2010_basis, ind_titles


    '''
    fuzzy_matching - function to match strings between IPUMS and ONET
    job titles using a similarity score threshold.
    Source: https://marcobonzanini.com/2015/02/25/fuzzy-string-matching-in-python/
    '''
    def fuzzy_matching(self):
        score_thresh = 100*self.fuzzy_threshold

        if self.job_list:
            title_list = self.job_list

        else:
            title_list = []

        matched_titles = []
        mismatched_titles = []

        # loop through IPUMS job titles
        for q in self.ipums_titles:
            # check if this job title is in our dictionary yet
            if q not in title_list:
                try:
                    '''
                    Method 1
                    '''
                    # Run a fuzz string comparison on this job title to all jobs in the ONET standard title list
                    fuzz_result = process.extract(q, self.onet_titles, limit=2)
                    # Initialize a success_counter to keep track if any good matches are found
                    success_counter = 0
                    # Loop through the top two choices
                    for option in fuzz_result:
                        if option[1] >= score_thresh:
                            # if the title score beats the threshold, add it to the saved title list
                            title_list.append([q, option[0]])
                            success_counter += 1

                    '''
                    Method 2
                    '''
                    # If neiter option is an exact match, try a different scoring metric
                    if success_counter == 0:
                        # Try a partial scoring method
                        alt_score_fuzz = process.extract(q, self.onet_titles, limit=2, scorer=fuzz.partial_ratio)

                        for option in alt_score_fuzz:
                            if option[1] >= score_thresh:
                                title_list.append([q, option[0]])
                                success_counter += 1

                    '''
                    Method 3
                    '''
                    # Try ONET alternate titles if no match was found yet
                    if success_counter == 0:
                        # Get the top two alternate title options
                        alt_fuzz = process.extract(q, self.onet_alt_titles['Alternate Title'], limit=2)
                        # Loop through the top two alternate choices
                        for option in alt_fuzz:
                            # Get the alternate job title with the highest similarity score
                            alt_job = self.onet_alt_titles['Title'][option[2]]
                            # If the similarity score for the alternate title is greater that 90%,
                            # then append it to the matched list and add it to the saved title list
                            if option[1] >= score_thresh:
                                matched_titles.append([q, alt_job, option[1], option[2]])
                                title_list.append([q, alt_job])
                                success_counter += 1

                    '''
                    Method 4
                    '''
                    # If no good match has been found, try a different scoring metric on the alternate titles
                    if success_counter == 0:
                        alt_score_alt_fuzz = process.extract(q, self.onet_alt_titles['Alternate Title'], limit=2, scorer=fuzz.partial_ratio)

                        for option in alt_score_alt_fuzz:
                            alt_job2 = self.onet_alt_titles['Title'][option[2]]
                            # If the similarity score for the alternate title with alt metric is greater that 90%,
                            # then append it to the matched list and add it to the saved title list
                            if option[1] >= score_thresh:
                                title_list.append([q, alt_job2])
                                success_counter += 1

                    # Record no good matches found for this title
                    if success_counter == 0:
                        mismatched_titles.append(q)
                except:
                    print('Fuzz Error with job title:', q)
                    mismatched_titles.append(q)


        print('Percentage of Titles Matched with 90+% Similarity Score:', round(100*(1-(len(mismatched_titles)/len(self.ipums_titles))),2),'%')
        return title_list, matched_titles, mismatched_titles

    '''
    match_user_input - function that reads a user input job title and optional
    riasec score and maps the title to a standard title in the ipums dictionary
    '''
    def match_user_input(self, user_jobs, user_riasec_scores=None):
        score_thresh = (100*self.fuzzy_threshold)

        # Initialize output holder lists
        output_titles = []
        output_riasec = []
        # Initialize temp data holder lists
        onet_fuzz = []
        scores = []

        # User provided two jobs
        if isinstance(user_jobs, list):
            for j in user_jobs:
                # Test for similar job titles in the ONET Alternate Titles dataset
                onet_alt_fuzz1 = process.extract(j, self.onet_alt_titles['Alternate Title'], limit=5)
                for m in onet_alt_fuzz1:
                    if m[1] >= score_thresh:
                        onet_title = self.onet_alt_titles['Title'][m[2]]
                        onet_fuzz.append(onet_title)
                        scores.append(m[1])

                # If we haven't found a good enough match yet, try a different similarity metric
                if not onet_fuzz:
                    onet_alt_fuzz2 = process.extract(j, self.onet_alt_titles['Alternate Title'], limit=5, scorer=fuzz.partial_ratio)
                    for n in onet_alt_fuzz2:
                        if n[1] >= score_thresh:
                            onet_title2 = self.onet_alt_titles['Title'][n[2]]
                            onet_fuzz.append(onet_title2)
                            scores.append(n[1])

                max_score = max(scores)
                max_idx = scores.index(max_score)
                best_job_match = onet_fuzz[max_idx]
                output_titles.append(best_job_match)
                output_riasec.append(self.get_user_riasec(best_job_match)[0])

            return output_titles, output_riasec

        # User provided one job and a RIASEC score
        elif (isinstance(user_jobs, str)) and (user_riasec_scores is not None):
            # Test for similar job titles in the ONET Alternate Titles dataset
            onet_alt_fuzz1 = process.extract(user_jobs, self.onet_alt_titles['Alternate Title'], limit=5)
            for m in onet_alt_fuzz1:
                if m[1] >= score_thresh:
                    onet_title = self.onet_alt_titles['Title'][m[2]]
                    onet_fuzz.append(onet_title)
                    scores.append(m[1])

            # If we haven't found a good enough match yet, try a different similarity metric
            if not onet_fuzz:
                onet_alt_fuzz2 = process.extract(user_jobs, self.onet_alt_titles['Alternate Title'], limit=5, scorer=fuzz.partial_ratio)
                for n in onet_alt_fuzz2:
                    if n[1] >= score_thresh:
                        onet_title2 = self.onet_alt_titles['Title'][n[2]]
                        onet_fuzz.append(onet_title2)
                        scores.append(n[1])

            max_score = max(scores)
            max_idx = scores.index(max_score)
            best_job_match = onet_fuzz[max_idx]
            output_titles.append(best_job_match)

            # Scale RIASEC values from the ONET Interest Profiler to match the stored data
            output_riasec = self.scale_riasec(user_riasec_scores)

            return output_titles, output_riasec

        else:
            print('Input Title and/or RIASEC score did not match required format!')



    '''
    job_title_to_industry_code - function that reads a user input job title and
    maps the title to a BLS industry code
    '''
    def job_title_to_industry_code(self, user_job):
        score_thresh = (100*self.fuzzy_threshold)

        # Initialize temp data holder lists
        scores = []
        bls_fuzz = []
        best_job_match = '10'

        bls_alt_fuzz1 = process.extract(user_job, self.ind_titles['industry_title'], limit=5)
        for m in bls_alt_fuzz1:
            if m[1] >= score_thresh:
                bls_code1 = self.ind_titles['industry_code'][m[2]]
                bls_fuzz.append(bls_code1)
                scores.append(m[1])

        if not bls_fuzz:
            onet_alt_fuzz2 = process.extract(user_job, self.ind_titles['industry_title'], limit=5, scorer=fuzz.partial_ratio)
            for n in onet_alt_fuzz2:
                if n[1] >= score_thresh:
                    bls_code2 = self.ind_titles['industry_code'][n[2]]
                    bls_fuzz.append(bls_code2)
                    scores.append(n[1])

        if len(scores) > 0:
            max_score = max(scores)
            max_idx = scores.index(max_score)
            best_job_match = bls_fuzz[max_idx]


        return best_job_match



    '''
    get_user_riasec - helper function that takes a given user input job and gets the
    corresponding RIASEC scores from the ONET Interest Score data
    '''
    def get_user_riasec(self, job_title):
        title_slice = self.titles_riasec_scores[self.titles_riasec_scores['ONET Title'] == job_title]
        return title_slice[['R','I','A','S','E','C']].to_numpy()



    '''
    get_user_ipums_code - function that takes a user input ONET job title and looks up the
    corresponding IPUMS job code
    '''
    def get_user_ipums_code(self, onet_title):
        title_slice = self.titles_riasec_scores[self.titles_riasec_scores['ONET Title'] == onet_title]
        onet_title = title_slice['ONET Title'].to_string(index=False).lstrip()
        ipums_fuzz = process.extractOne(onet_title, self.ipums_titles)
        ipums_code = self.ipums_code_titles[self.ipums_code_titles['Title'] == ipums_fuzz[0]]['Code'].to_string(index=False).lstrip()
        return ipums_code


    '''
    scale_riasec - function that scales a user input RIASEC score from the ONET
    Interest Profiler to meet the scale of our dataset (0-40 -> 0-7)
    '''
    def scale_riasec(self, score_set):
        return [round(7*(x/40),2) for x in score_set]


    '''
    write_title_dict - function to write the title matching dataframe to a
    tab-separated text file.
    '''
    def write_title_dict(self, title_list):
        if self.job_list is not None:
            # Ask for user confirmation before allowing append access
            response = input('Existing Job Title Matching file detected. Do you want to append to the file? (y/n): ')
            if response.lower() == 'y':
                self.access_mode = 'a'
            elif response.lower() == 'n':
                self.access_mode = 'r'

        if self.access_mode == 'w':
            # Convert the Title list to a Dataframe and save it to a text file for later
            # Access mode is write if no file was previously detected, otherwise it is append only acces
            title_match_df = pd.DataFrame(title_list).reset_index(drop=True)
            title_match_df.columns = ['IPUMS Title', 'ONET Title']
            title_match_df.to_csv(self.match_dict_path, header=title_match_df.columns, index=None, sep='\t', mode=self.access_mode)
        else:
            print('File not written, access mode is not valid')
