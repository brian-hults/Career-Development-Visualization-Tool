# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 10:52:35 2020

BLS API Test

@author: Brian Hults
"""
# import packages
import urllib.request
import urllib
import pandas as pd


class BLS_Query:
    def __init__(self, year='2019', qtr='3', area_titles_path=None, \
                 ind_titles_path=None):

        if area_titles_path is None:
            self.area_titles_path = 'area_titles.csv'
        else:
            self.area_titles_path = area_titles_path

        if ind_titles_path is None:
            self.ind_titles_path = 'industry_titles.csv'
        else:
            self.ind_titles_path = ind_titles_path

        self.area_code_dict = self.readAreaCodes()
        self.ind_code_dict = self.readIndCodes()
        self.year = year
        self.qtr = qtr



    '''
    query_top_emp_jobs - function to query the BLS QCEW API for the top n industries
    in a given area by percentage of employment level for the most recently available
    quarter of data (currently 2019 Q3)
    '''
    def query_top_emp_jobs(self, code_area, top_n=10, ind_res=4, own_type='private', \
                       area_data=None):

        if area_data is None:
            # Get data from the input area
            area_data = self.qcewGetAreaData(code_area)

        # Using the input area code, ownership type, and industry resolution, get
        # the appropriate BLS aggregation codes and ownership code
        own_code, agg_codes = self.parse_area_ind_codes(code_area, own_type, ind_res)

        # Get data from the input area
        area_df = pd.DataFrame(area_data[1:], columns=area_data[0])

        # Filter out non-disclosed companies/industries
        filter1 = area_df[(area_df['disclosure_code'] != 'N') | (area_df['lq_disclosure_code'] != 'N')]

        # Filter for a given resolution of industry level (default is NAICS 4 digit industry)
        filter2 = filter1[filter1['industry_code'].str.len() == ind_res]

        # Filter for a type of compnay ownership (default is private)
        filter3 = filter2[filter2['own_code']==own_code]

        # Filter for the level of aggregation code
        filtered_df = filter3[filter3['agglvl_code'].isin(agg_codes)]

        # Map the area title, industry title, and calculate the desired statistics for each area/industry
        area_title = filtered_df['area_fips'].map(self.area_code_dict)
        ind_title = filtered_df['industry_code'].map(self.ind_code_dict)
        
        # Remove the industry title codes from the output data using regex string replacement
        ind_title = ind_title.str.replace(r'^(\d+|[a-zA-Z]+|[a-zA-Z]+\d+) (\d+ )*', '')

        # Get monthly employment levels and percentages
        monthly_emp_lvls = filtered_df[['month1_emplvl', 'month2_emplvl', 'month3_emplvl']].apply(pd.to_numeric)
        avg_emp_lvl = monthly_emp_lvls.mean(axis=1)
        total_employed = avg_emp_lvl.sum()
        pct_emp_lvl = avg_emp_lvl.divide(total_employed).multiply(100).round(2)
        
        # Get avg weekly wages for those top industries
        avg_wkly_wage = filtered_df['avg_wkly_wage'].apply(pd.to_numeric)

        # Compute the estimated yearly wage
        est_year_wage = avg_wkly_wage.multiply(52)

        # Convert the Average Employment levels to a int to remove the trailing decimals
        avg_emp_lvl_str = avg_emp_lvl.astype(int)

        # Gather desired results in a final dataframe
        results_df = pd.DataFrame({'area_title': area_title, \
                                   'industry_title': ind_title, \
                                   'avg_emp_lvl': avg_emp_lvl_str, \
                                   'pct_emp_lvl': pct_emp_lvl,  \
                                   'avg_wkly_wage': avg_wkly_wage, \
                                   'est_year_wage': est_year_wage})

        # Sort by largest percentage of employment level
        sorted_results = results_df.sort_values(axis=0, by='pct_emp_lvl', ascending=False).to_numpy()
        top_n_results = sorted_results[:top_n,:]

        return top_n_results



    '''
    query_top_wage_jobs - function to query the BLS QCEW API for the top n industries
    in a given area by average weekly wages, with estimates for yearly wages included,
    for the most recently available quarter of data (currently 2019 Q3)
    '''
    def query_top_wage_jobs(self, code_area, top_n=10, ind_res=4, own_type='private', \
                        area_data=None):

        if area_data is None:
            # Get data from the input area
            area_data = self.qcewGetAreaData(code_area)

        # Using the input area code, ownership type, and industry resolution, get
        # the appropriate BLS aggregation codes and ownership code
        own_code, agg_codes = self.parse_area_ind_codes(code_area, own_type, ind_res)

        # Convert the area data to a dataframe
        area_df = pd.DataFrame(area_data[1:], columns=area_data[0])

        # Filter out non-disclosed companies/industries
        filter1 = area_df[(area_df['disclosure_code'] != 'N') | (area_df['lq_disclosure_code'] != 'N')]

        # Filter for a given resolution of industry level (default is NAICS 4 digit industry)
        filter2 = filter1[filter1['industry_code'].str.len() == ind_res]

        # Filter for a type of compnay ownership (default is private)
        filter3 = filter2[filter2['own_code']==own_code]

        # Filter for the level of aggregation code
        filtered_df = filter3[filter3['agglvl_code'].isin(agg_codes)]

        # Map the area title, industry title, and calculate the desired statistics
        # for the area/industry
        area_title = filtered_df['area_fips'].map(self.area_code_dict)
        ind_title = filtered_df['industry_code'].map(self.ind_code_dict)
        
        # Remove the industry title codes from the output data using regex string replacement
        ind_title = ind_title.str.replace(r'^(\d+|[a-zA-Z]+|[a-zA-Z]+\d+) (\d+ )*', '')

        # Get the average weekly wage
        avg_wkly_wage = filtered_df['avg_wkly_wage'].apply(pd.to_numeric)

        # Compute the estimated yearly wage
        est_year_wage = avg_wkly_wage.multiply(52)

        # Gather desired results in a final dataframe
        results_df = pd.DataFrame({'area_title': area_title, \
                                   'industry_title': ind_title, \
                                   'avg_wkly_wage': avg_wkly_wage, \
                                   'est_year_wage': est_year_wage})

        # Sort by largest percentage of employment level
        sorted_results = results_df.sort_values(axis=0, by='avg_wkly_wage', ascending=False).to_numpy()
        top_n_results = sorted_results[:top_n,:]

        return top_n_results



    '''
    query_ind_data - function to query for specific industry data across various areas
    '''
    def query_ind_data(self, code_ind, code_area, ind_res=4, own_type='private', \
                       ind_data=None):

        if ind_data is None:
            ind_data = self.qcewGetIndustryData(code_ind)

        # Get industry resolution by type of input industry code
        if 'NAICS' in self.ind_code_dict[code_ind]:
            ind_res = len(code_ind)
        # If the scope is wider than NAICS codes, just include the default 3-code
        else:
            ind_res = 3

        # Using the input area code, ownership type, and industry resolution, get
        # the appropriate BLS aggregation codes and ownership code
        own_code, agg_codes = self.parse_area_ind_codes(code_area, own_type, ind_res)

        # Convert the area data to a dataframe
        ind_df = pd.DataFrame(ind_data[1:], columns=ind_data[0])

        # Filter out non-disclosed companies/industries
        filter1 = ind_df[(ind_df['disclosure_code'] != 'N') | (ind_df['lq_disclosure_code'] != 'N')]


        # Filter for a given resolution of industry level (default is NAICS 4 digit industry)
        filter2 = filter1[filter1['industry_code'] == code_ind]

        # Filter for a type of compnay ownership (default is private)
        filter3 = filter2[filter2['own_code']==own_code]
        
        # Filter for the industry in a specific area code
        filter4 = filter3[filter3['area_fips'] == code_area]

        # Filter for the level of aggregation code
        filtered_df = filter4[filter4['agglvl_code'].isin(agg_codes)]

        return filtered_df.to_numpy()



    ###########################
    # BLS QCEW Helper Functions
    ###########################

    '''
    parse_area_ind_codes - helper function that takes an input area and industry
    type to scope the required BLS API inputs for other query functions
    '''
    def parse_area_ind_codes(self, code_area, own_type='private', ind_res=4):

        own_type = own_type.lower()
        own_dict = {'total covered': 0, 'private': 5, 'international government': 4,
                    'local government': 3, 'state government': 2, 'federal government': 1,
                    'total government': 8}

        # Check for valid ownership type, and get ownership code
        if own_type not in own_dict:
            print('This ownership type is not a valid choice! Choices include:', own_dict.keys())
        else:
            out_own_code = str(own_dict[own_type])

        # Check the scope of the area code to determine agg level code
        national_codes = ['US000', 'USCMS', 'USMSA', 'USNMS']
        if code_area in national_codes:
            # Select national level aggregation codes
            out_agg_codes = ['10', '11', '12', '13']
            # Add in the NAICS industry code by input resolution
            out_agg_codes.append(str(ind_res+12))

        # Check to see if it is a state code
        elif 'state' in self.area_code_dict[code_area].lower():
            # Select statewide level aggregation codes
            out_agg_codes = ['50', '51', '52', '53']
            # Add in the NAICS industry code by input resolution
            out_agg_codes.append(str(ind_res+52))

        # Check if we have a county code
        elif 'county' in self.area_code_dict[code_area].lower():
            # Select county level aggregation codes
            out_agg_codes = ['70', '71', '72', '73']
            # Add in the NAICS industry code by input resolution
            out_agg_codes.append(str(ind_res+72))

        else:
            print('No aggregation code found for this area code!')

        return out_own_code, out_agg_codes


    # *******************************************************************************
    # qcewCreateDataRows : This function takes a raw csv string and splits it into
    # a two-dimensional array containing the data and the header row of the csv file
    # a try/except block is used to handle for both binary and char encoding
    def qcewCreateDataRows(self, csv):
        dataRows = []
        try:
            dataLines = csv.decode().split('\r\n')
        except:
            dataLines = csv.split('\r\n')

        for row in dataLines:
            stripped_row = row.replace('"','')
            dataRows.append(stripped_row.split(','))
        return dataRows
    # *******************************************************************************




    # *******************************************************************************
    # qcewGetAreaData : This function takes a year, quarter, and area argument and
    # returns an array containing the associated area data. Use 'a' for annual
    # averages.
    # For all area codes and titles see:
    # http://www.bls.gov/cew/doc/titles/area/area_titles.htm
    #
    def qcewGetAreaData(self, area):
        urlPath = "http://data.bls.gov/cew/data/api/[YEAR]/[QTR]/area/[AREA].csv"
        urlPath = urlPath.replace("[YEAR]",self.year)
        urlPath = urlPath.replace("[QTR]",self.qtr.lower())
        urlPath = urlPath.replace("[AREA]",area.upper())
        httpStream = urllib.request.urlopen(urlPath)
        csv = httpStream.read()
        httpStream.close()
        #print('CSV:', csv)
        return self.qcewCreateDataRows(csv)
    # *******************************************************************************


    # *******************************************************************************
    # qcewGetIndustryData : This function takes a year, quarter, and industry code
    # and returns an array containing the associated industry data. Use 'a' for
    # annual averages. Some industry codes contain hyphens. The CSV files use
    # underscores instead of hyphens. So 31-33 becomes 31_33.
    # For all industry codes and titles see:
    # http://www.bls.gov/cew/doc/titles/industry/industry_titles.htm
    #
    def qcewGetIndustryData(self, industry):
        urlPath = "http://data.bls.gov/cew/data/api/[YEAR]/[QTR]/industry/[IND].csv"
        urlPath = urlPath.replace("[YEAR]",self.year)
        urlPath = urlPath.replace("[QTR]",self.qtr.lower())
        urlPath = urlPath.replace("[IND]",industry)
        httpStream = urllib.request.urlopen(urlPath)
        csv = httpStream.read()
        httpStream.close()
        return self.qcewCreateDataRows(csv)
    # *******************************************************************************


    # *******************************************************************************
    # qcewGetSizeData : This function takes a year and establishment size class code
    # and returns an array containing the associated size data. Size data
    # is only available for the first quarter of each year.
    # For all establishment size classes and titles see:
    # http://www.bls.gov/cew/doc/titles/size/size_titles.htm
    #
    def qcewGetSizeData(self, size):
        urlPath = "http://data.bls.gov/cew/data/api/[YEAR]/1/size/[SIZE].csv"
        urlPath = urlPath.replace("[YEAR]",self.year)
        urlPath = urlPath.replace("[SIZE]",size)
        httpStream = urllib.request.urlopen(urlPath)
        csv = httpStream.read()
        httpStream.close()
        return self.qcewCreateDataRows(csv)
    # *******************************************************************************


    # *******************************************************************************
    # readAreaCodes : This function reads the full list of available area codes for
    # all available counties, states, and the whole US from the given CSV file and
    # outputs a dictionary to map the titles to codes.
    def readAreaCodes(self):
        try:
            area_data = pd.read_csv(self.area_titles_path)
        except:
            print('area_titles.csv: File not found!')

        return area_data.set_index('area_fips')['area_title'].to_dict()
    # *******************************************************************************


    # *******************************************************************************
    # readIndCodes : This function reads the full list of available industry codes
    # for all available counties, states, and the whole US from the given CSV file
    # and outputs a dictionary to map the titles to codes.
    def readIndCodes(self):
        try:
            ind_data = pd.read_csv(self.ind_titles_path)
        except:
            print('industry_titles.csv: File not found!')

        return ind_data.set_index('industry_code')['industry_title'].to_dict()
    # *******************************************************************************