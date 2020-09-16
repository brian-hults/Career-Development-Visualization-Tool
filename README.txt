#############################################################
CSE 6242 Team 44 (Witty Goldfish) Project Deliverables README
#############################################################

###########
LINK TO DEMO VIDEO
###########
https://www.youtube.com/watch?v=4M1lOPqZFTk&feature=youtu.be

###########
DESCRIPTION
###########

This code base is designed and built to fulfill the functional requirements
of the Career Development Visualization Tool as described in our report.
This package is structured in a series of programs that first extract and
read training data files acquired from the IPUMS Current Population Survey,
then process that data into a useable format, and then split and run the data
into several classifier models to predict results. This code base also includes
a program built to query the Bureau of Labor Statistics API for generic employment
statistics for our mapping tool.

(If you would like to request a copy of the academic report, please email hultsb@gmail.com)

###### Instructions on how to download data from IPUMS CPS ######
Our training dataset is available for download from the IPUMS CPS website
and can be accessed via the following steps.
1) Navigate to the IPUMS CPS home page: https://cps.ipums.org/cps/
2) Click the 'LOG IN' button in the top right corner
3) Click the 'Create an account' option. (Required to download data, but the data extracts are free)
4) Fill out the form and click 'Submit', you will need to verify your email
address before proceeding.

After creating an account:
1) Navigate back to the IPUMS CPS home page: https://cps.ipums.org/cps/
2) Click on the 'Select Data' tab
3) Click 'Search' under the 'Select Variables' section
4) Type in 'OCC' and click Search
5) Click the 'Plus' icon next to the two variables: 'OCC2010' and 'OCC10LY'
with corresponding Variable Labels of Occupation, 2010 basis and Occupation
last year, 2010 basis. This will add both of those variables to your cart.
6) To add more variables to your cart, Click 'Search' under the
'Select Variables' section again
7) Type in 'CPSID' and click Search
8) Click the 'Plus' icon next to the two variables 'CPSID' and 'CPSIDP'
that have the labels household record and person record.
9) After selecting all of these variables, click the 'Select Samples' button
10) In the ASEC data selection screen, select all years from 1968 to present
and then click the 'Submit Sample Selections' button at the bottom of the screen.
11) Click the 'View Cart' button on the hovering summary of 'Your Data Extract'

Note: In order to keep only necessary variables and minimize the downloaded file
size, we recommend deselecting all add-on variables in the cart. If you wish to
track the sample year or other metrics, you can retain the respective variables.

12) Deselect the 'Check' icon for all variables you don't want included in the
downloaded sample.
13) Click the 'Create Data Extract' button at the top of the screen. This will
take you to an 'Extract Request' page to review and confirm all details.
14) On the 'Extract Request' page, click the 'Change' button for the Data format
and select '.csv'. Optionally add a description of the extract, and click
'Submit Extract' at the bottom of the page.
15) You should now be redirected to the Downloads page, and you should see a
'Processing...' bar next to the requested data sample. CPS samples can take
several minutes to generate, but the system will send an email to your account
email address when it is ready for download.
14) When the sample is ready, navigate back to the 'My Data' page of the
IPUMS CPS website and download the CSV file and the DDI file for extraction.

IPUMS CPS Data Selection and Extraction Instructions Reference:
https://cps.ipums.org/cps/instructions.shtml

###### Data Extraction ######
The data downloaded from the IPUMS website is extracted via the 'ipumsr' package
for R Studio (documentation at the link below). We set up a short program in
'extract_ipums_data.R' that takes the DDI file associated with the sample data
from IPUMS and extracts the CSV file from the compressed '.gz' file format.
The program also filters the data for NA values in the last two job code
columns before writing the data set to a tab-separated text file for later use.

CRAN ipumsr package documentation:
https://cran.r-project.org/web/packages/ipumsr/ipumsr.pdf
https://cran.r-project.org/web/packages/ipumsr/vignettes/ipums.html

###### IPUMS and ONET Information and RIASEC Scores ######
The O*NET database maintains a mapping of occupations (via the O*NET-SOC codes)
to Interest ratings. For all occupations included in the O*NET database, an
occupational interest profile was created by experts. These experts assigned
numerical values to each of the six interest areas used in the RIASEC model.
The six interest areas in the model include: Realistic, Investigative,
Artistic, Social, Enterprising and Conventional. When a person uses our Career
Development Visualization Tool, their previous job history as well as their
personal interest profile is compared to the occupational  interest profiles
to recommend other occupations.

The occupational interest profile data set in the O*NET database includes the
SOC codes that are also part of the IPUMS to O*NET title mapping discussed in
section above. These two data sets are linked together based on this
field. Below is link to the code used to perform this mapping.

Additional information on the O*NET Interests data:
https://www.onetcenter.org/dictionary/24.2/excel/interests.html

Additional information about the mapping of IPUMS OCC2010 codes to Census
occupation codes (SOC codes used by O*NET):
https://cps.ipums.org/cps/occ_transition_2002_2010.shtml
https://usa.ipums.org/usa/chapter4/chapter4.shtml


###### BLS API Query Program ######
This program is used to support the visual functionality of the mapping tool,
and is used whether or not users have generated a profile and received career
recommendations. It queries the Bureau of Labor Statistics API to retreive
sample industry statistics such as the top five industries by employement levels
in a given county. This information is used to populate informative charts in
our user interface to relay important information about industries in the area
around a user's location.



###### CLASSIFIERS ######

###### KNN Classifier ######
Subsequent to the pre-processing performed by the clf_driver.py program and the separation into X_train, X_test, y_train and y_test by the sklearn.model_selection.train_test_split function, parameters were tuned for KNN modeling. The tuning and modeling were performed by the use of the sklearn.model_selection.GridSearchCV and sklearn.neighbors.KNeighborsClassifier functions, respectively.

The tuning was performed using a value of three for k-fold cross-validation and scoring was performed using “roc_auc_ovr”. The “roc_auc_ovr” scoring  computes the area under the receiver operating characteristic curve (ROC AUC) according to the online documentation at https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html#sklearn.metrics.roc_auc_score. Also according to the documentation, the AUC is computed for each class against the rest of the classes.

In addition to the tuning settings discussed in paragraph above, the parameters and values checked during tuning are the following:
•	n_neighbors: Neighbors between 3 and 401 were incremented by 2 and checked. Then, to speed up the process, neighbors were incremented by 20 from 601 to 901, and then by 100 from 1001 to 2001. Eventually, 1701 was found to be the best number of neighbors as the AUC began converging to 0.986 at that number.
•	weights: Uniform and Distance. Uniform was selected as it consistently had better AUC values.

According to the online documentation at https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html, n_neighbors is the number of neighbors to use, uniform weights indicates that all points in each neighborhood are weighted equally, and when ‘distance’ is used for the weights, closer neighbors will have greater influence than points further away.


##### Random Forest Classifier #####

The data was subject to the same pre-processing described in the above KNN section. In addition, "one-versus-rest" ROC AUC was used in determining the validity of the model as well. The tuning parameters used were as follows:

•	criterion: Gini and entropy, as we learned in class. These two were shown to have very little difference on the ROC AUC score and as such we used the default value of Gini.
•	n_estimators: Values from 1 to 501 were tested, incremented by 50. 51 was shown to be the optimal value by the elbow method as it had a 0.032 increase in ROC AUC over just 1 tree using the Gini criteria, and increasing all the way to 501 (which held the highest ROC AUC) only resulted in an increase of 0.01 with a training time 10x that of the 51 tree model.


###### Gaussian Naive Bayes Model ######

The data was subject to the same pre-processing described in the above KNN section. In addition, "one-versus-rest" ROC AUC was used in determining the validity of the model as well. Due to the nature of GNB, no tuning was performed and the default scikit-learn values were used with no informative prior probabilities being specified.

###########
INSTALLATION
###########
LOCAL INSTALLATION AND EXECUTION SHOULD ONLY BE USED AS A BACKUP IF THE HOSTED SITE IS DOWN. TO ACCESS THE FULL HOSTED SITE, PLEASE VISIT: http://wittygoldfish.pythonanywhere.com/

The 'Web Source' directory contains all necessary files to host the web application locally or on a remote server. The web application utilized the Python library Flask and the directory follows the structure outlined below:

The Web Source Directory contains all files needed to launch the web application and execute all of the backend methods. The following files are included:
/Web Source/Alternate Titles.txt
/Web Source/area_titles.csv
/Web Source/bls_qcew_api.py
/Web Source/clf_driver.py
/Web Source/flask_app.py
/Web Source/Interests.txt
/Web Source/industry_titles.csv
/Web Source/ipums_job_title_codes_2010_basis.txt
/Web Source/job_title_matching.py
/Web Source/job_title_matching_dictionary.txt
/Web Source/numeric_occupation_data_1968_present.txt
/Web Source/Occupation Data.txt
/Web Source/onet_ipums_job_to_riasec_scores.txt
/Web Source/onet_ipums_title_to_riasec.py
/Web Source/onet_job_to_riasec_scores.txt

The Templates folder contains the html code used to generate the UI. The following file is included:
/Web Source/templates/index.html

The static folder contains the json file used to generate the map visualization and a file denoting state identification codes:
/Web Source/static/counties-10m.json
/Web Source/static/state_fips.csv

The assets folder is empty by default but is used to hold files created by the application that are shared between the python and html code:
/Web Source/assets/

If for any reason a local installation is necessary, please use the following steps to launch the site:

BEFORE STARTING: Folow the instructions to download and extract BLS data. place the ipums_job_title_codes_2010_basis.txt file in the Web Source directory before starting the installation process.

1. Use the following commands to install dependencies on your machine:
 1a. 'pip install Flask' (or 'pip3 install Flask' if using pip3)
 1b. 'pip install fuzzywuzzy'(or 'pip3 install fuzzywuzzy' if using pip3)
2. Clone this repo onto your machine using 'git clone https://github.gatech.edu/btesser3/CSE-6242-Team-Witty-Goldfish-Project.git'
3. Download this file - https://drive.google.com/uc?id=1yBSG6YlMQXDBb4BOA09hv5-5upGSCZfv&export=download (sorry about the 274MB file size!) - and move it to 'CSE-6242-Team-Witty-Goldfish-Project\Web Source'
4. Using the terminal, navigate to the 'Web Source' directory using 'cd "CSE-6242-Team-Witty-Goldfish-Project\Web Source"'
5. Using Python 3, run the flask_app.py file. (ex: python3 flask_app.py)
6. The site may take 5-6 minutes to launch. Once complete, you should see something similar to the following:
   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
7. Navigate to the provided URL (ex: http://127.0.0.1:5000/) in your browser. The webpage may take some time to load.
8. Move to Step 1 in the Execution section to continue.

###########
EXECUTION
###########
The website can be viewed and tested by navigating to the following URL: http://wittygoldfish.pythonanywhere.com/
After navigating to the website, follow the below instructions to test the functionality:

1. In the Job History text box, enter one or more previous job titles.
2. If you have not done so already, navigate to the O*Net Interest Profiler Quiz (https://www.mynextmove.org/explore/ip) and answer the provided questions.
3. After completing the quiz, select your scores for each section using the drop downs.
4. Click the 'Submit' button.
5. The model may take a few seconds to process the data. Once the prediction is completed, you next predicted job will be displayed.
6. After recieving your predicted job, you may click on the map to view areas with a number of these jobs available.
  6a. Clicking on a state will zoom in to display the counties in a state.
  6b. Clicking on a county wil open a tool tip displaying relevant job information in the county.
  6c. To reset the map, the user can click on a county twice, click outside of the map, or click the reset button in the bottom right hand corner of the page.
