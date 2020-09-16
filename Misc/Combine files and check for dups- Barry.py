#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


ipums_occ_data_codes = pd.read_csv("./data/numeric_occupation_data_1968_present.txt",sep="\t")
ipums_occ_data_codes


# In[3]:


ipums_occ_data_codes2 = ipums_occ_data_codes[ipums_occ_data_codes.OCC2010 != ipums_occ_data_codes.OCCLY2010]
ipums_occ_data_codes2


# In[4]:


ipums_job_titles = pd.read_csv("./data/ipums_job_title_codes_2010_basis.txt",sep="\t")
ipums_job_titles


# In[5]:


result = pd.merge(ipums_occ_data_codes2, ipums_job_titles, left_on='OCC2010', right_on='Code', how='outer')
result


# In[ ]:





# In[6]:


result.drop('Code', axis=1, inplace=True)
result


# In[7]:


job_titles_matched = pd.read_csv("./data/job_title_matching_dictionary.txt",sep="\t")
job_titles_matched


# In[8]:


result2 = pd.merge(result, job_titles_matched, left_on='Title', right_on='IPUMS Title', how='inner')
result2


# In[9]:


result2.drop(['Title', 'Fuzzy Score', 'ONET File Index'], axis=1, inplace=True)
result2


# In[10]:


ONET_RAISEC_scores = pd.read_csv("./data/ONET_job_to_RAISEC_scores.txt",sep="\t", names=["Title", "R", "I", "A", "S", "E", "C"])
ONET_RAISEC_scores


# In[11]:


result3 = pd.merge(result2, ONET_RAISEC_scores, left_on='ONET Title', right_on='Title', how='inner')
result3


# In[12]:


result4 = result3[result3.I.notnull()]
result4


# In[13]:


result4b = result4.copy()
result4b[['Rk', 'Realistic']] = result4b.R.str.split(":", expand=True)
result4b[['Ik', 'Investigative']] = result4b.I.str.split(":", expand=True)
result4b[['Ak', 'Artistic']] = result4b.A.str.split(":", expand=True)
result4b[['Sk', 'Social']] = result4b.S.str.split(":", expand=True)
result4b[['Ek', 'Enterprising']] = result4b.E.str.split(":", expand=True)
result4b[['Ck', 'Conventional']] = result4b.C.str.split(":", expand=True)


# In[14]:


print(result4b)


# In[15]:


result5 = result4b.copy()

result5['Realistic'] = result5['Realistic'].replace('}', '', regex=True)
result5['Realistic'] = result5['Realistic'].astype(float)

result5['Investigative'] = result5['Investigative'].replace('}', '', regex=True)
result5['Investigative'] = result5['Investigative'].astype(float)

result5['Artistic'] = result5['Artistic'].replace('}', '', regex=True)
result5['Artistic'] = result5['Artistic'].astype(float)

result5['Social'] = result5['Social'].replace('}', '', regex=True)
result5['Social'] = result5['Social'].astype(float)

result5['Enterprising'] = result5['Enterprising'].replace('}', '', regex=True)
result5['Enterprising'] = result5['Enterprising'].astype(float)

result5['Conventional'] = result5['Conventional'].replace('}', '', regex=True)
result5['Conventional'] = result5['Conventional'].astype(float)

print(result5)


# In[16]:


result5.drop(['R', 'I', 'A', 'S', 'E', 'C', 'Rk', 'Ik', 'Ak', 'Sk', 'Ek', 'Ck'], axis=1, inplace=True)
print(result5)


# In[43]:


result5.dtypes


# In[53]:


ipums_occ_data_codes_cp = ipums_occ_data_codes.copy()
ipums_occ_data_codes_cp.CPSIDP = ipums_occ_data_codes_cp.CPSIDP.astype(str)
ipums_occ_data_codes_cp2 = ipums_occ_data_codes_cp[(ipums_occ_data_codes_cp.CPSIDP != 'nan') & (ipums_occ_data_codes_cp.CPSIDP != '0.0')]


# In[54]:


ipums_code_dups = ipums_occ_data_codes_cp2[ipums_occ_data_codes_cp2.duplicated(subset=['CPSIDP'], keep=False)]
ipums_code_dups.sort_values(by=['CPSIDP', 'YEAR'])


# In[ ]:


ipums_occ_data_codes_cp.dtypes


# In[57]:


#Test of duplicate
ipums_code_dups[ipums_code_dups.CPSIDP == '20180307223602.0']


# In[60]:


#Check how many unique duplicate instances
ipums_code_dups_unique = ipums_occ_data_codes_cp2[ipums_occ_data_codes_cp2.duplicated(subset=['CPSIDP'], keep='first')]
ipums_code_dups_unique




