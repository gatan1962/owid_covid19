import streamlit as st
from datetime import timedelta, datetime
import urllib.request
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

#ReaMe: To generate selected data to track,
#       run this program. it will download source data from OWI site
#       and write the selected data into a data consolidated file.
    
######################################################
######## download data from OWID web-site  ############
######################################################
data_url = ('https://covid.ourworldindata.org/data/owid-covid-data.csv')

## To get latest update from data_url
r = requests.get(data_url)
st.write('Last update:', r.headers['Date'])

@st.cache
def load_data(country='Malaysia'):
    data = pd.read_csv(data_url, nrows=None)
    
    # change all columns string to lowercase
    lower_case = lambda x: str(x).lower()
    data.rename(lower_case, axis='columns', inplace=True)
    country_list = sorted(set(data['location']))
       
    # convert date from string to datetime
    data['date'] = pd.to_datetime(data['date']).dt.date
    
    # select country data of interest
    country_data = data[data['location'] == country]
    
    return country_data, country_list

def check_raw_data(input_data, header):
    st.subheader(header)
    st.write(input_data)

## program initialization
st.title('Covid-19 Trend Chart')
st.text('Data source:- https://covid.ourworldindata.org/data/owid-covid-data.csv')

## User input country name
country_name = st.text_input('Enter country:')
country_name = " ".join(country_name.split()) # keep single space between components of name

## Download covid data from owid url
data, country_list = load_data(country_name) 

if country_name not in country_list:
    st.warning('Please enter country to proceed...')
    st.write('Selected country is:', country_name)

## use a button to toggle country names
if st.checkbox('Show all country names'):
    check_raw_data(country_list, 'List of sorted country names:')
    
if st.checkbox('Raw data'):
    check_raw_data(data, 'Raw data of selected country')  

######################################################
######## 1. Define data of interest       ############
######################################################
y_label = ['new_cases', 'new_deaths', 'weekly_hosp_admissions', 'positive_rate']
x = data['date']
y_nc, y_nd, y_wh = data[y_label[0]], data[y_label[1]], data[y_label[2]]

## check if weekly_hosp_admission data available
y_wh_lst = y_wh.tolist() # convert df to list object
y_wh_data = [d for d in y_wh_lst if str(d).replace('.','',1).isdigit()] # keep if data available
y_wh_data = len(y_wh_data) > 0 # bool:True if data exist.

##################################################################
######## 2. Generate chart with user select start date        ####
##################################################################
x_lst = list(x) # type: datetime

st.info('Slide to select Start Date:')
try:
    start_date = st.slider('', x_lst[0], x_lst[-1],\
                           format='YYYY/MM/DD') # use direct as datetime object
    date_index = x_lst.index(start_date)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
    x1 = x_lst[date_index:]
    y1 = y_nc[date_index:]
    y2 = y_nd[date_index:]
    y3 = y_wh[date_index:]
    freq = int(len(x1)//30) + 1
    ticks, country = freq, country_name

    ## Plot charts:
    fig, ax = plt.subplots(3, 1, figsize=(8,10)) # 2 charts align in column
    ax[0].scatter(x1, y1)
    ax[1].scatter(x1, y2)  
    ax[2].scatter(x1, y3, marker='.', color='g')
    
    ## Standardized x-limit & x-ticks for all charts
    days = timedelta(int(0.03 * len(x1)) + 1) # off-set days
    ax[0].set_xlim(x1[0] - days, x1[-1] + days)
    ax[1].set_xlim(x1[0] - days, x1[-1] + days)
    ax[2].set_xlim(x1[0] - days, x1[-1] + days)

    ## Plot 1st chart:
    ax[0].set_title(country)
    ax[0].set_xlabel('')
    ax[0].set_ylabel(y_label[0])
    ax[0].yaxis.set_label_coords(-0.1, 0.5) # set y-label position
    ax[0].set_xticks(x1[::ticks])
    ax[0].set_xticklabels([])
    ax[0].grid(linestyle='--')
    
    ## Plot 2nd chart:
    #ax[1].set_xlabel('Date')
    ax[1].set_ylabel(y_label[1])
    ax[1].yaxis.set_label_coords(-0.1, 0.5)
    ax[1].set_xticks(x1[::ticks])
    ax[1].set_xticklabels([])    
    ax[1].grid(linestyle='--')
    
    ## Plot 3rd chart:
    if y_wh_data: # bool: if data available
        
        ax[2].set_xlabel('Date', fontsize=12)
        ax[2].set_ylabel(y_label[2])
        ax[2].yaxis.set_label_coords(-0.1, 0.5)
        ax[2].set_xticks(x1[::ticks])
        ax[2].set_xticklabels(x1[::ticks], rotation=90, fontsize=8)
        ax[2].grid(linestyle='--')
       
    else:
        y_dummy = [0 for k in y3] #generate dummy data. To avoid x-ticks squeeze
        y3 = y_dummy
        ax[2].scatter(x1, y3, marker='')
        ax[2].annotate(text='>>> data not available <<<', xy = (0.35,0.55), \
                       xycoords='axes fraction', fontsize=12)
        ax[2].set_ylabel(y_label[2])
        ax[2].yaxis.set_label_coords(-0.1, 0.5)
        ax[2].set_xticks(x1[::ticks])
        ax[2].set_xticklabels(x1[::ticks], rotation=90, fontsize=8)
        ax[2].grid(linestyle='--')
    
    fig.tight_layout()
    st.pyplot(fig)
    
except Exception as e:
    st.warning('Oops...! Please check if country is entered correctly.')
