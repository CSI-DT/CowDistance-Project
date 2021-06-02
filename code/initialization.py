######################################################################################################
# Author: Yuna Otrante-Chardonnet
# Start: April 17th 2021
# Title: initialization.py
# Description: 
# This code alows to create a dataframe from a csv file and to create a sub-dataframe for a given cow.
# It can also fill in the missing data to reduce the computation's inaccuracies 
######################################################################################################

import pandas as pd
from scipy.interpolate import Akima1DInterpolator
import numpy as np
import functions as func

pd.options.mode.chained_assignment = None  # default='warn'

# Function create a dataframe from a CSV file
def csv_read(file):
    header_list = ["data_entity", "tag_id", "tag_string", "epoch_time", "x", "y", "z"]
    df = pd.read_csv(file, names=header_list)
    df = func.detect_drop_inactive_tags(df) #Drop inactive tags
    return df

# Function to test to get all the histogram of 6 cows
def csv_read_bis(file):
    header_list = ["data_entity", "tag_id", "tag_string", "epoch_time", "x", "y", "z"]
    df = pd.read_csv(file, names=header_list)
    df = df[df['tag_id']>2433132] # there is 6 cows above this tag id
    return df

# Function to retrieve cow information
def csv_read_cow(file):
    header_list = ["data_entity", "tag_id", "tag_string", "epoch_time", "x", "y", "z","rounded_time"]
    df = pd.read_csv(file, names=header_list)
    return df

# Function to get the feeding areas coordinates and return the matching rows of the dataframe
def feeding_area(df_cow,barn):
    # Feeding area 1
    f1_x1 = int(barn[barn['Unit']=='feed1']['x1'])
    f1_x2 = int(barn[barn['Unit']=='feed1']['x3'])
    f1_y1 = int(barn[barn['Unit']=='feed1']['y1'])
    f1_y2 = int(barn[barn['Unit']=='feed1']['y2'])

    # Feeding area 2
    f2_x1 = int(barn[barn['Unit']=='feed2']['x1'])
    f2_x2 = int(barn[barn['Unit']=='feed2']['x3'])
    f2_y1 = int(barn[barn['Unit']=='feed2']['y1'])
    f2_y2 = int(barn[barn['Unit']=='feed2']['y2'])

    return df_cow[((df_cow['x'].between(f1_x1,f1_x2)) & (df_cow['y'].between(f1_y1,f1_y2))) | ((df_cow['x'].between(f2_x1,f2_x2)) & (df_cow['y'].between(f2_y1,f2_y2)))]

# Function to get the bedding areas coordinates and return the matching rows of the dataframe
def bedding_area(df_cow,barn):
    ls = []
    units = list(barn['Unit'])
    # Get index of each bed
    for i in range (len(units)):
        if units[i].startswith('bed'):
            ls.append(i)

    # Set lists of the coordinates of all beds
    x_1 = list(barn[barn.index.isin(ls)]['x1'])
    x_2 = list(barn[barn.index.isin(ls)]['x3'])
    y_1 = list(barn[barn.index.isin(ls)]['y1'])
    y_2 = list(barn[barn.index.isin(ls)]['y2'])


    bet_x, bet_y = [], []

    for i in range (len(df_cow)):
        for j in range (len(x_1)):
            # If a row of the dataframe is between the coordinates
            if x_1[j] <= df_cow['x'][i] <= x_2[j] and y_1[j] <= df_cow['y'][i] <= y_2[j]:
                bet_x.append(df_cow['x'][i])
                bet_y.append(df_cow['y'][i])    

    return df_cow[(df_cow['x'].isin(bet_x)) & (df_cow['y'].isin(bet_y))]

# Function to get the cubicle areas coordinates and return the matching rows of the dataframe
def cubicle_area(df_cow,barn):
    r1_x1 = int(barn[barn['Unit']=='cubicle1']['x1'])
    r1_x2 = int(barn[barn['Unit']=='cubicle1']['x3'])
    r1_y1 = int(barn[barn['Unit']=='cubicle1']['y1'])
    r1_y2 = int(barn[barn['Unit']=='cubicle1']['y2'])

    r2_x1 = int(barn[barn['Unit']=='cubicle2']['x1'])
    r2_x2 = int(barn[barn['Unit']=='cubicle2']['x3'])
    r2_y1 = int(barn[barn['Unit']=='cubicle2']['y1'])
    r2_y2 = int(barn[barn['Unit']=='cubicle2']['y2'])

    return df_cow[((df_cow['x'].between(r1_x1,r1_x2)) & (df_cow['y'].between(r1_y1,r1_y2))) | ((df_cow['x'].between(r2_x1,r2_x2)) & (df_cow['y'].between(r2_y1,r2_y2)))]

# Function to get the alley coordinates and return the matching rows of the dataframe
def alley(df_cow,barn):
    df1 = feeding_area(df_cow,barn)
    df2 = bedding_area(df_cow,barn)
    df3 = cubicle_area(df_cow,barn)

    df4 = pd.concat([df1,df2,df3])
    return df_cow.merge(df4, how = 'outer' ,indicator='Ind').loc[lambda x : x['Ind']=='left_only'].drop(columns=['Ind'])

# Function to  return the matching rows of the dataframe between the given coordinates
def custom_area(df_cow,x1,x2,y1,y2):
    return df_cow[((df_cow['x'].between(x1,x2)) & (df_cow['y'].between(y1,y2)))]

# Function to delimite the barn and the different areas
def area_delimitation(df_cow,area):
    barn = pd.read_csv("../data/barn.csv", skiprows = 0, sep = ';', header=0)
    barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3','y4']

    b1_x1 = int(barn[barn['Unit']=='Base']['x1'])
    b1_x2 = int(barn[barn['Unit']=='Base']['x3'])
    b1_y1 = int(barn[barn['Unit']=='Base']['y1'])
    b1_y2 = int(barn[barn['Unit']=='Base']['y2'])

    ind = df_cow[(df_cow['x'] < b1_x1) | (df_cow['x'] > b1_x2) | (df_cow['y'] < b1_y1) | (df_cow['y'] > b1_y2)].index
    df_cow.drop(ind , inplace=True)
    df_cow.reset_index(drop=True, inplace=True)

    if area == "feeding":
        return feeding_area(df_cow,barn)

    elif area == "bedding":
        return bedding_area(df_cow,barn)

    elif area == "cubicle":
        return cubicle_area(df_cow,barn)

    elif area == "alley":
        return alley(df_cow,barn)
    
    return df_cow

# Function create a subset from a dataframe matching the given tag id,starting and ending epoch time and area  
def create_cow(cow_id,df,e_min,e_max,area):
    df_cow = df[(df['tag_id']==cow_id) & (df['epoch_time']>=e_min*1000) & (df['epoch_time']<e_max*1000)]
    df_cow = area_delimitation(df_cow,area)
    df_cow.reset_index(drop=True, inplace=True)
    df_cow['rounded_time'] = (df_cow['epoch_time']/1000).astype(int) # rounded time to remove the milliseconds 
    return df_cow

# Function to add the missing coordinates to the dataframe by data interpolation
def create_coordinates(df_cow,i,time_gap,t,t2,x2,y2):
    time = 1000
    ls = []
    td = int(time_gap[i])
    for j in range (1,td):
        ind = np.where(t2 == t[i-1]+j)
        xf = int(x2[ind])
        yf = int(y2[ind])
        ls.append(['FA_ADD', df_cow['tag_id'].loc[i], df_cow['tag_string'].loc[i], df_cow['epoch_time'].loc[i-1] + time, round(xf), round(yf), df_cow['z'].loc[i], int((df_cow['epoch_time'].loc[i-1] + time)/1000)])
        time += 1000
    return ls

# Function compute the missing data
def fill_data(df_cow,area):
    if df_cow.empty is False:    
        df_cow.drop_duplicates(subset ='rounded_time', keep = 'first', inplace = True)
        df_cow.reset_index(drop=True, inplace=True)

        # Create subset of all time gaps of more than 1 second
        time_gap = df_cow['rounded_time'].diff()[df_cow['rounded_time'].diff()>1]
        difference = df_cow[df_cow['rounded_time'].diff()>1]
        index = difference.index
        list_coord = []

        t = df_cow['rounded_time'].to_numpy()
        t2 = np.arange(t[0], t[-1], 0.1)
        t2 = np.around(t2, decimals=1)

        # Data interpolation
        x = df_cow['x'].to_numpy()
        x2 = Akima1DInterpolator(t, x)(t2)
        y = df_cow['y'].to_numpy()
        y2 = Akima1DInterpolator(t, y)(t2)

        # For each gap in the dataframe (>1 second)
        for i in index:
            list_coord += create_coordinates(df_cow,i,time_gap,t,t2,x2,y2)

        df_cow = df_cow.append(pd.DataFrame(list_coord, columns=df_cow.columns), ignore_index=True)
        # Make sure the coordinates are not out of range
        df_cow = area_delimitation(df_cow,area)
        df_cow.drop_duplicates(subset ='rounded_time', keep = 'first', inplace = True)
        df_cow = df_cow.sort_values(by=['rounded_time'])
        df_cow.reset_index(drop=True, inplace=True)

    return df_cow