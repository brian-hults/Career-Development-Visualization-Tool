import json
import os
import os.path
from os import path
import urllib.parse
import numpy as np
import bls_qcew_api as b
import clf_driver as c
import job_title_matching as m
from flask import Flask, jsonify, render_template, request
app = Flask(__name__)


bls = b.BLS_Query(area_titles_path="area_titles.csv", ind_titles_path="industry_titles.csv")
driver = c.CLF_Driver(validation=True, train_size=0.7, job_data_path="numeric_occupation_data_1968_present.txt", ipums_titles_path="ipums_job_title_codes_2010_basis.txt", ipums_onet_riasec_scores_path="onet_ipums_job_to_riasec_scores.txt")
str_matcher = m.Title_Matching(ipums_title_codes_path="ipums_job_title_codes_2010_basis.txt", occ_data_path="Occupation Data.txt", alt_titles_path="Alternate Titles.txt", match_dict_path="job_title_matching_dictionary.txt", riasec_scores_path="onet_job_to_riasec_scores.txt", ind_titles_path="industry_titles.csv")



@app.route('/')
def index():
    driver.train_RandomForest()
    #str_matcher = m.Title_Matching(ipums_title_codes_path="ipums_job_title_codes_2010_basis.txt", occ_data_path="Occupation Data.txt", alt_titles_path="Alternate Titles.txt", match_dict_path="job_title_matching_dictionary.txt", riasec_scores_path="onet_job_to_riasec_scores.txt")
    #fuzz_job_title_list, fuzz_matched_jobs, fuzz_mismatched_jobs = str_matcher.fuzzy_matching()
    f = open("static/rf.csv", "w")
    f.write("rf trained")
    f.close()
    return render_template('index.html')

@app.route('/getIndData')
def getIndData():
    arg = request.args.get('x', '')
    print(arg)
    args = arg.split(",")
    #industry code, area code
    ind_code = str_matcher.job_title_to_industry_code(arg[0])
    data = bls.query_ind_data(ind_code, args[1])
    f = open("static/indData.csv", "w")

    data = np.asarray(data)

    s = ""
    for x in range(len(data[0])):
        s = s + "i" + str(x) + "\t"
    s = s + "\n"
    for i in data:
        for j in i:
            s = s + str(j) + "\t"
        s = s + "\n"

    f.write(s)
    f.close()
    return "Nothing"

@app.route('/getMultiIndData')
def getMultiIndData():
    arg1 = request.args.get('x', '')
    arg2 = request.args.get('y', '')

    areas = arg2.split(",")
    #industry code, area code
    ind_code = str_matcher.job_title_to_industry_code(arg1)

    f = open("static/multiIndData.csv", "w")

    data = bls.query_ind_data(ind_code, areas[0])

    data = np.asarray(data)
    s = ""
    for x in range(len(data[0])):
        s = s + "i" + str(x) + "\t"
    s = s + "\n"

    for area in areas:
        data = bls.query_ind_data(ind_code, area)
        data = np.asarray(data)
        for i in data:
            for j in i:
                s = s + str(j) + "\t"
            s = s + "\n"

    f.write(s)
    f.close()
    return "Nothing"

@app.route('/getWageData')
def getWageData():
    #bls = b.BLS_Query(area_titles_path="area_titles.csv", ind_titles_path="industry_titles.csv")
    arg = request.args.get('x', '')
    print(arg)
    data = bls.query_top_wage_jobs(arg, top_n=3)
    f = open("static/wageData.csv", "w")
    s = ""
    for x in range(len(data[0])):
        s = s + "i" + str(x) + "\t"
    s = s + "\n"
    for i in data:
        for j in i:
            s = s + str(j) + "\t"
        s = s + "\n"

    #f.write(str(data))
    f.write(s)
    f.close()
    print(data)
    return "Nothing"

@app.route('/getEmpData', methods= ['GET',  'POST'])
def getEmpData():
    arg = request.args.get('x', '')
    print(arg)
    data = bls.query_top_emp_jobs(arg, top_n=3)
    f = open("static/empData.csv", "w")

    s = ""
    for x in range(len(data[0])):
        s = s + "i" + str(x) + "\t"
    s = s + "\n"
    for i in data:
        for j in i:
            s = s + str(j) + "\t"
        s = s + "\n"

    #f.write(str(data))
    f.write(s)
    f.close()

    return "Nothing"

@app.route('/getClfData')
def getClfData():

    #parse args
    job = request.args.get('x', '')
    raisec = request.args.get('y', '')
    #array of jobs
    jobs = job.split(",")
    #array of raisec scores
    raisecs = raisec.split(",")
    for i in range(0, len(raisecs)):
        raisecs[i] = int(raisecs[i])


    if len(raisecs) < 2:
        #user input with two jobs
        #test_jobs = ['Lab Manager', 'Mechanical Engineer']
        user_titles, user_riasec = str_matcher.match_user_input(jobs)
        user_ipums_code1 = str_matcher.get_user_ipums_code(user_titles[0])
        test_point = np.hstack([user_ipums_code1, user_riasec[0], user_riasec[1]])
    elif len(raisecs) > 2:
        #user input with a single job and RIASEC scores
        #test_riasec = [19,25,5,5,6,19] # Quiz scores can be on a scale to a max of 40. The program will scale them down to match the dataset
        user_titles, user_riasec = str_matcher.match_user_input(jobs[0], raisecs)
        user_ipums_code = str_matcher.get_user_ipums_code(user_titles[0])
        scaled_test_riasec = str_matcher.scale_riasec(raisecs)
        test_point = np.hstack([user_ipums_code, user_riasec, scaled_test_riasec])



    pred = driver.predict(driver.rf_model, test_point, drop=True)#driver.X_test.iloc[0,:])
    f = open("static/clfData.csv", "w")

    pred = np.asarray(pred)

    s = ""
    for x in range(len(pred[0])):
        s = s + "i" + str(x) + "\t"
    s = s + "\n"
    for i in pred:
        for j in i:
            s = s + str(j) + "\t"
        s = s + "\n"

    f.write(s)
    f.close()
    print(pred)
    return "Nothing"

#Delete CLF file
@app.route('/delCLF')
def delCLF():
    if path.exists("static/clfData.csv"):
        os.remove("static/clfData.csv")
    if path.exists("/static/clfData.csv"):
        os.remove("/static/clfData.csv")
    return "Nothing"


if __name__ == '__main__':

    app.run()
