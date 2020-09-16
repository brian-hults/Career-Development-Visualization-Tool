# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 19:26:51 2020
CSE 6242 Team Project - Classification Driver
@author: Brian Hults, Alex Arnon, Barry Tesser
"""

# Import packages
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score
import time

class CLF_Driver:
    def __init__(self, train_size=0.8, validation=False, drop=True, seed=42, \
                 job_data_path=None, ipums_titles_path=None, \
                 ipums_onet_riasec_scores_path=None):

        # Set data file paths
        if job_data_path is None:
            self.job_data_path = 'numeric_occupation_data_1968_present.txt'
        else:
            self.job_data_path = job_data_path

        if ipums_titles_path is None:
            self.ipums_titles_path = 'ipums_job_title_codes_2010_basis.txt'
        else:
            self.ipums_titles_path = ipums_titles_path

        if ipums_onet_riasec_scores_path is None:
            self.ipums_onet_riasec_scores_path = 'onet_ipums_job_to_riasec_scores.txt'
        else:
            self.ipums_onet_riasec_scores_path = ipums_onet_riasec_scores_path


        self.seed = seed
        np.random.seed(seed)
        self.train_size = train_size
        self.k_neighbors = 1701

        # Read in the data
        data = self.read_data()
        self.job_data = data[0]
        self.ipums_titles = data[1]
        self.ipums_onet_riasec_scores = data[2]

        # Filter and Process the datasets
        prepped_data = self.filter_and_process_data(validation, drop)

        # Map different outputs if we need a validation set or not
        if validation:
            self.X_train = prepped_data[0]
            self.X_valid = prepped_data[1]
            self.X_test = prepped_data[2]
            self.y_train = prepped_data[3]
            self.y_valid = prepped_data[4]
            self.y_test = prepped_data[5]
            self.codes_scores_df = prepped_data[6]
        else:
            self.X_train = prepped_data[0]
            self.X_test = prepped_data[1]
            self.y_train = prepped_data[2]
            self.y_test = prepped_data[3]
            self.codes_scores_df = prepped_data[4]




    '''
    read_data - function to read in the required data files
    '''
    def read_data(self):
        try:
            # Read in the training data
            job_data = pd.read_csv(self.job_data_path, sep='\t', header=0, dtype=str)
            # Read in the IPUMS  title
            ipums_job_titles = pd.read_csv(self.ipums_titles_path, sep='\t', dtype=str, na_values=['Unknown'])
            ipums_job_titles.dropna(axis=0, how='any', inplace=True)
            # Read in the map from job codes and titles to RIASEC scores
            ipums_onet_riasec_scores = pd.read_csv(self.ipums_onet_riasec_scores_path,sep="\t", dtype=str, header=0)
            
            return job_data, ipums_job_titles, ipums_onet_riasec_scores
        except:
            print('One of three required files was not found!')



    '''
    read_and_prep_data - function to create the map from IPUMS and
    ONET titles to RIASEC scores, and then split the data into train, test, and
    an optional validation set.
    '''
    def filter_and_process_data(self, validation=False, drop=False):
        # Filter down to only records where the individual changed job codes
        transition_data = self.job_data[self.job_data['OCC2010'] != self.job_data['OCCLY2010']]

        # Merge training data with corresponding RIASEC scores
        occly_codes_scores_df = pd.merge(transition_data, self.ipums_onet_riasec_scores, left_on='OCCLY2010', right_on='IPUMS Code', how='inner')
        occly_codes_scores_df.drop(['YEAR', 'CPSID', 'CPSIDP', 'IPUMS Title', 'ONET Title', 'IPUMS Code'], axis=1, inplace=True)
        occly_codes_scores_df.rename(columns={'R': 'R_ly', 'I': 'I_ly', 'A': 'A_ly', 'S': 'S_ly', 'E': 'E_ly', 'C': 'C_ly'}, inplace=True)
        codes_scores_df = pd.merge(occly_codes_scores_df, self.ipums_onet_riasec_scores, left_on='OCC2010', right_on='IPUMS Code', how='inner')
        codes_scores_df.drop(['IPUMS Title', 'ONET Title', 'IPUMS Code'], axis=1, inplace=True)

        # Drop duplicate records of the same job transition
        # codes_scores_df.drop_duplicates(subset=['OCC2010', 'OCCLY2010'], inplace=True)

        # Split into X features and y labels
        X = codes_scores_df.iloc[:,1:]
        y = codes_scores_df.iloc[:,0]

        # One Hot Encode OCCLY2010 or drop it depending on the value passed to drop
        if drop:
            X = X.drop(columns=['OCCLY2010'])
        else:
            X = pd.get_dummies(X, prefix='OCCLY2010', columns=['OCCLY2010'])

        if validation:
            # Split the data into training and remainder sets
            X_train, X_remainder, y_train, y_remainder = train_test_split(X, y, train_size=self.train_size, random_state=self.seed)
            # Split the remainder data evenly into validation and test sets
            X_valid, X_test, y_valid, y_test = train_test_split(X_remainder, y_remainder, test_size=0.5, random_state=self.seed)

            return X_train, X_valid, X_test, y_train, y_valid, y_test, codes_scores_df

        else:
            # Split the data into training and test sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=self.train_size, random_state=self.seed)

            return X_train, X_test, y_train, y_test, codes_scores_df




    ############################
    # Classifier 1 Here
    def train_RandomForest(self):
        train_time = time.time()
        self.rf_model = RandomForestClassifier(random_state=self.seed).fit(self.X_train, self.y_train)
        print('Random Forest Model Trained in {} seconds!'.format(round(time.time()-train_time,2)), '\n')
    ############################



    ############################
    # Classifier 2 Here
    def train_GNB(self):
        train_time = time.time()
        self.gnb_model = GaussianNB().fit(self.X_train, self.y_train)
        print('Gaussian Naive Bayes Model Trained in {} seconds!'.format(round(time.time()-train_time,2)), '\n')
    ############################



    ############################
    # Classifier 3 Here
    def train_KNN(self):
        train_time = time.time()
        self.knn_model = KNeighborsClassifier(n_jobs=-1, n_neighbors=self.k_neighbors).fit(self.X_train, self.y_train)
        print('K-Nearest Neighbors Model Trained in {} seconds!'.format(round(time.time()-train_time,2)), '\n')
    ############################



    def validate_models(self):
        valid_time1 = time.time()
        rf_probas = self.rf_model.predict_proba(self.X_valid)
        self.rf_auc = roc_auc_score(self.y_valid, rf_probas, multi_class='ovr')
        print('Random Forest roc auc: {}'.format(self.rf_auc),
              '\nValidation Completed in {} seconds'.format(round(time.time()-valid_time1,2)), '\n')

        valid_time2 = time.time()
        gnb_probas = self.gnb_model.predict_proba(self.X_valid)
        self.gnb_auc = roc_auc_score(self.y_valid, gnb_probas, multi_class='ovr')
        print('Gaussian NB roc auc: {}'.format(self.gnb_auc),
              '\nValidation Completed in {} seconds'.format(round(time.time()-valid_time2,2)), '\n')

        valid_time3 = time.time()
        knn_probas = self.knn_model.predict_proba(self.X_valid)
        self.knn_auc = roc_auc_score(self.y_valid, knn_probas, multi_class='ovr')
        print('KNN roc auc: {}'.format(self.knn_auc),
              '\nValidation Completed in {} seconds'.format(round(time.time()-valid_time3,2)), '\n')


    def test_model(self, chosen_model):
        test_time = time.time()
        test_probas = chosen_model.predict_proba(self.X_test)
        self.test_model_auc = roc_auc_score(self.y_test, test_probas, multi_class='ovr')
        print('Test Model roc auc: {}'.format(self.test_model_auc),
              '\nTesting Completed in {} seconds'.format(round(time.time()-test_time,2)))



    def predict(self, chosen_model, X_test, drop=False):
        pred_time = time.time()
        
        # Drop the job code depending on the value passed to drop
        if drop:
            X_test = X_test[1:]
        
        if (len(X_test.shape) == 1):
            X_test_arr = np.array(X_test).reshape(1,-1)
            pred = chosen_model.predict(X_test_arr)
            pred_info = self.get_job_info(pred)
        else:
            X_test_arr = np.array(X_test)
            preds = chosen_model.predict(X_test_arr)
            pred_info = []
            for p in preds:
                pred_info.append(self.get_job_info(p))

        print('Prediction Completed in {} seconds'.format(round(time.time()-pred_time,2)))
        return pred_info



    def get_job_info(self, code):
        try:
            return self.ipums_onet_riasec_scores[self.ipums_onet_riasec_scores['IPUMS Code'] == code[0]]
        except:
            print('Job code not found in database!')
