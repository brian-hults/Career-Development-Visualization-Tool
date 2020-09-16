import pandas as pd

data = pd.read_csv('job_title_transition_dataset.csv')
transition_dict = {}


for index, row in data.iterrows():

    this_year = row['Occupation this year']
    last_year = row['Occupation last year']

    if this_year not in transition_dict:
        transition_dict[this_year] = {}
    
    if last_year in transition_dict[this_year]:
        transition_dict[this_year][last_year] += 1
    else:
        transition_dict[this_year][last_year] = 1

ordered_transition_dict = {}

for job, sub_dict in transition_dict.items():
    print(sub_dict)
    ordered_sub_dict = sorted(sub_dict.items(), key=lambda item: item[1], reverse=True)

    ordered_transition_dict[job] = ordered_sub_dict

print(ordered_transition_dict)