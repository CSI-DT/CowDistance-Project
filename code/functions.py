'''
This is a file containing all functions needed to perform the analysis of
the data.

FUNCTION CATAGORIES IN ORDER:
    *read csv-files
    *divide cows into groups/remove tags
    *plots
    *metrics
    *animation
    *other
    
Written by Torsten and Björn
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
import math
import matplotlib.lines as mlines
import matplotlib.patches as pat
from matplotlib.animation import FuncAnimation
from matplotlib import transforms
from datetime import datetime

###############################################################################
####                     READ CSV-FILES                                   #####
###############################################################################
 
def csv_read_FA(filename, nrows):
    if nrows == 0:
        df = pd.read_csv(filename, header=None)
    else:
        df = pd.read_csv(filename, nrows=nrows, header=None)
    df.columns = ['data_entity', 'tag_id', 'tag_string', 'time', 'x', 'y', 'z']
    return df

def csv_read_PA(filename, nrows):
    if nrows == 0:
        df = pd.read_csv(filename, header=None)
    else:
        df = pd.read_csv(filename, nrows=nrows, header=None)
    df.columns = ['data_entity', 'tag_id', 'tag_string', 'start', 'end', 'x', 'y', 'z', 'activity_type', 'distance']
    return df

def csv_read_PAA(filename, nrows):
    if nrows == 0:
        df = pd.read_csv(filename, header=None)
    else:
        df = pd.read_csv(filename, nrows=nrows, header=None)
    df.columns = ['data_entity', 'tag_id', 'tag_string', 'span', 'interval', 'activity_type', 'distance', 'periods',
                  'duration']
    return df

def csv_read_PC(filename, nrows):
    if nrows == 0:
        df = pd.read_csv(filename, header=None)
    else:
        df = pd.read_csv(filename, nrows=nrows, header=None)
    df.columns = ['data_entity', 'tag_id', 'tag_string', 'start', 'end', 'x', 'y', 'z']
    return df

###############################################################################
####                     SUBSET COWS/DROP TAGS/OTHER                      #####
###############################################################################

# functions to get all ids for cows in the data
def unique_cows(df):
    return df.tag_id.unique()

# function to drop rows with certain tag_ids
def drop_tags(df, tags_filename):
    tags = pd.read_csv(tags_filename, skiprows = 0, sep = ';', header=0)
    tags.columns = ['position', 'Zx', 'Zy', 'tag_string', 'tag_id']
    tag_ids = list(tags['tag_id'])
    for i in range(len(tag_ids)):
        df = df.drop(df[df.tag_id == tag_ids[i]].index)
    return df

# function to remove ceratin tags in the dataframe
def remove_tags(df, tags):
    for c in tags:
        df = df[df.tag_id != c]
    return df

# function to divide cows into left and right    
def left_right(df, barn_filename):
    barn = pd.read_csv(barn_filename, skiprows = 0, sep = ';', header=0)
    barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3','y4']
    left_wall = list(barn['x1'])[0]
    right_wall = list(barn['x3'])[0]
    u_cows = unique_cows(df)
    right = []
    left = []
    for i in range(len(u_cows)):
        temp = df.loc[df['tag_id'] == u_cows[i]]
        x,y,z = positions(temp)
        if sum(x)/len(x) <= left_wall + (right_wall+left_wall)/2:
            left.append(u_cows[i])
            
        else:
            right.append(u_cows[i])

    left_df = df[df['tag_id'].isin(left)]
    right_df = df[df['tag_id'].isin(right)]
    return left_df, right_df

# function to divide cows into groups based on bed preference
def divide_cows(df, barn_filename):

    u_cows = unique_cows(df)   #Get a list of the unique cows ID:s

    barn = pd.read_csv(barn_filename, skiprows=0, sep=';', header=0)            #Read the barn beds coordinates
    barn.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4']

    bed1 = barn.iloc[7]         #divide the different beds
    bed2 = barn.iloc[8]
    bed3 = barn.iloc[9]
    bed4 = barn.iloc[10]
    bed5 = barn.iloc[11]
    bed6 = barn.iloc[12]
    bed8 = barn.iloc[13]
    bed9 = barn.iloc[14]

    beds = {0: [],   #Initiate lists of cows
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: []}

    for i in range(len(u_cows)):        #For each cow that has activity type "In cubicle"
        temp = df.loc[df['tag_id'] == u_cows[i]]
        temp = temp.loc[temp['activity_type'] == 3]
        x, y, z = positions(temp)   #Get the positions from the cow
        bed_count = [0]*8

        for j in range(len(x)): #For each position, assign it to a bed
            if is_inside((x[j], y[j]), bed1):
                bed_count[0] += 1
            elif is_inside((x[j], y[j]), bed2):
                bed_count[1] += 1
            elif is_inside((x[j], y[j]), bed3):
                bed_count[2] += 1
            elif is_inside((x[j], y[j]), bed4):
                bed_count[3] += 1
            elif is_inside((x[j], y[j]), bed5):
                bed_count[4] += 1
            elif is_inside((x[j], y[j]), bed6):
                bed_count[5] += 1
            elif is_inside((x[j], y[j]), bed8):
                bed_count[6] += 1
            elif is_inside((x[j], y[j]), bed9):
                bed_count[7] += 1

        if sum(bed_count) != 0:         #If the cow has been in any bed, append its ID to the list of the bed where it spent the most time
            beds[bed_count.index(max(bed_count))].append(u_cows[i])
        else:
            beds[8].append(u_cows[i])   #If none of the cows 'in cubicle' positions could be assigned to a bed, or if there where none, assign to separate list

    return list(beds.values())      #Return a list of lists of the ID:s of cows in different beds

# help function
def is_inside(pos, bed):
    if bed['x1'] < pos[0] < bed['x3'] and bed['y1'] < pos[1] < bed['y2']:
        return True
    else:
        return False
    
# function to detect and drop inactive tags for PA-data
def detect_drop_inactive_tags(df):
    ucows = unique_cows(df)
    to_drop = []
    for cow in ucows:
        temp = df.loc[df['tag_id'] == cow]
        x,y,z = positions(temp)
        if abs(max(y)-min(y)) <= 1: # only check y-direction
            to_drop.append(cow)
    
    for i in range(len(to_drop)):
        df = df.drop(df[df.tag_id == to_drop[i]].index) # drop tags

    return df

###############################################################################
####                               PLOTS                                  #####
###############################################################################

# function to plot the outline of the barn
def plot_barn(filename):
        df = pd.read_csv(filename, skiprows = 0, sep = ';', header=0)
        df.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3','y4']
        units = list(df['Unit'])
        x_1 = list(df['x1'])
        x_2 = list(df['x2'])
        x_3 = list(df['x3'])
        x_4 = list(df['x4'])
        y_1 = list(df['y1'])
        y_2 = list(df['y2'])
        y_3 = list(df['y3'])
        y_4 = list(df['y4'])

        fig, ax = plt.subplots(1,figsize=(6,6))
        for i in range(len(units)):
           art =  pat.Rectangle((x_1[i],min(y_1[i],y_2[i])),x_3[i]-x_1[i], max(y_1[i],y_2[i])-min(y_1[i],y_2[i]), fill = False)
           ax.add_patch(art)
           #print(ax.patches)
        ax.set_xlim(x_1[0]-2000,x_3[0]+2000)
        ax.set_ylim(y_1[0]-2000,y_2[0]+2000)
        return fig, ax
    
def plot_barnV2(filename):
        df = pd.read_csv(filename, skiprows = 0, sep = ';', header=0)
        df.columns = ['Unit', 'x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3','y4']
        units = list(df['Unit'])
        x_1 = list(df['x1'])
        x_2 = list(df['x2'])
        x_3 = list(df['x3'])
        x_4 = list(df['x4'])
        y_1 = list(df['y1'])
        y_2 = list(df['y2'])
        y_3 = list(df['y3'])
        y_4 = list(df['y4'])

        fig, ax = plt.subplots(1,figsize=(8,5))
        for i in range(len(units)):
           art =  pat.Rectangle((y_2[i],max(x_2[i],x_3[i])),y_4[i]-y_2[i], min(x_2[i],x_3[i])-max(x_2[i],x_3[i]), fill = False)
           ax.add_patch(art)
           #print(ax.patches)
        ax.set_xlim(x_1[0]-2000,x_3[0]+2000)
        ax.set_ylim(y_1[0]-2000,y_2[0]+2000)
        return fig, ax

def plot_all_cows(ax, df_FA, time, exceptions):
    id_to_plot = []
    row_to_plot = []
    special_cows_id = []
    special_cows_index = []
    count = 0
    incident_position = []

    cow_1 = df_FA.loc[df_FA['tag_id'] == exceptions[0]]

    row_exception = cow_1.loc[cow_1['time'] == time]

    posx = row_exception['x'].values[0]
    posy = row_exception['y'].values[0]


    for index, row in df_FA.iterrows(): #for all rows in the data,
        if abs(row['time']-time)<10000 and row['tag_id'] not in id_to_plot and row['tag_id'] not in exceptions: #if they are within 10 seconds before or after and not already found or one of the interesting cows
            id_to_plot.append(row['tag_id'])
            row_to_plot.append(count)
            if 10000000>abs(row[4]-posx) and 1000000>abs(row[5]-posy): #if they are within
                special_cows_id.append(row['tag_id'])
                special_cows_index.append(count)
        count += 1

    cows_to_plot = df_FA.iloc[row_to_plot]

    return ax, special_cows_id


# function to plot the position of a cow (based on tag_id) for FA-data
def plot_cow(df, tag_id, filename_barn):
    fig, ax = plot_barn(filename_barn)
    if hasattr(tag_id, "__len__"):
        for i in tag_id:
            temp = df.loc[df['tag_id'] == i]
            x,y,z = positions(temp)
            plt.plot(x,y,'o--', markersize = 2)
    else:
        temp = df.loc[df['tag_id'] == tag_id]
        x,y,z = positions(temp)
        plt.plot(x,y,'o--', markersize = 2)
    plt.show()
   
# function to plot the distance between two cows
def plot_distance(df, tag_id1, tag_id2):
    cow_1 = df.loc[df['tag_id'] == tag_id1]
    cow_2 = df.loc[df['tag_id'] == tag_id2]
    x1,y1,z1 = positions(cow_1)
    x2,y2,z2 = positions(cow_2)
    
    times_1 = list(cow_1['time'])
    times_2 = list(cow_2['time'])
    
    distance_x = []
    distance_y = []
    
    distance_x.append(x1[0] - x2[0]) # initial distance
    distance_y.append(y1[0] - y2[0])
    i = 0 # index of times_1/x1/y1
    j = 0 # index of times_2/x2/y2
    times_comb = []
    times_comb.append(min(times_1[0], times_2[0]))
    while i < len(times_1)-1 or j < len(times_2)-1:
        if times_1[i] <= times_2[j]:           
            if i == len(times_1)-1:# if at end of times_1
                j = j+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2[j],times_1[i]))
            else:
                i = i+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2[j],times_1[i]))
        else:
            if j == len(times_2)-1: # if at end of times_2
                i = i+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2[j],times_1[i]))
            else:
                j = j+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2[j],times_1[i]))

    distance = []
    temp = times_comb[0]
    times_comb = [x - temp for x in times_comb] # set initial time to zero
    times_comb_plot = [x*1/(3600*1000) for x in times_comb] 

    for i in range(len(distance_x)):
        distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))
    fig, ax =  plt.subplots(1,figsize=(6,6))
    ax.plot(times_comb_plot, distance)
    ax.set_title('Distance between cow ' + str(tag_id1) + ' and ' + str(tag_id2))
    plt.show()
    hist_arr = np.zeros(times_comb[-1])
    index = 0
    for i in range(len(times_comb)-1):
        hist_arr[index:times_comb[i+1]] = distance[i]
        index = times_comb[i+1]

    plt.hist(hist_arr, bins=50)
    plt.show()
    
def plot_cow_PAv2(df, tag_id, filename_barn):
    fig, ax = plot_barn(filename_barn)
    temp = df.loc[df['tag_id'] == tag_id]
    x, y, z, activity = positions_PA(temp)
    current_activity = activity[0]
    for i in range(len(activity)):
        if activity[i] != current_activity:
            plt.plot(x[i], y[i], 'o--', markersize=2, color='k')

def plot_cow_PA(df, tag_id, filename_barn):
    fig, ax = plot_barn(filename_barn)
    if hasattr(tag_id, "__len__"):
        for id in tag_id:
            temp = df.loc[df['tag_id'] == id]
            x, y, z, activity = positions_PA(temp)
            for i in range(len(activity)):
                if activity[i] == 0:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='k')
                elif activity[i] == 1:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='b')
                elif activity[i] == 2:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='y')
                elif activity[i] == 3:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='r')
                elif activity[i] == 4:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='g')
                elif activity[i] == 5:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='m')
                else:
                    plt.plot(x[i], y[i], 'o--', markersize=2, color='c')
    else:
        temp = df.loc[df['tag_id'] == tag_id]
        x, y, z, activity = positions_PA(temp)
        for i in range(len(activity)):
            if activity[i] == 0:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='k')
            elif activity[i] == 1:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='b')
            elif activity[i] == 2:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='y')
            elif activity[i] == 3:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='r')
            elif activity[i] == 4:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='g')
            elif activity[i] == 5:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='m')
            else:
                plt.plot(x[i], y[i], 'o--', markersize=2, color='c')


    Blue = mlines.Line2D([], [], color='b', marker='.',
                            markersize=15, label='Standing')
    Yellow = mlines.Line2D([], [], color='y', marker='.',
                         markersize=15, label='Walking')
    Red = mlines.Line2D([], [], color='r', marker='.',
                           markersize=15, label='In cubicle')
    Green = mlines.Line2D([], [], color='g', marker='.',
                           markersize=15, label='At feed')
    Magenta = mlines.Line2D([], [], color='m', marker='.',
                           markersize=15, label='At drinker')
    Cyan = mlines.Line2D([], [], color='c', marker='.',
                           markersize=15, label='Outside')
    Black = mlines.Line2D([], [], color='k', marker='.',
                          markersize=15, label='Unknown')
    plt.legend(handles=[Blue, Yellow, Red, Green, Magenta, Cyan, Black])

    plt.show()



# function to plot all cows in a time interval
def plot_time(df, t1, t2):
    temp = df.loc[df['time'] <= t2]
    temp = temp.loc[df['time'] >= t1]
    x,y,z = positions(temp)
    plt.scatter(x,y, s = 2)
    plt.show()
        

# function to plot cows based on PC-data    
def plot_cow_PC(df, tag_id, filename_barn):       
    fig, ax = plot_barn(filename_barn)
    if hasattr(tag_id, "__len__"):
        colors = []
        for i in range(len(tag_id)):
            colors.append('#%06X' % randint(0, 0xFFFFFF))
                          
        zip_object_tag_col = zip(tag_id, colors)
        for i,c in zip_object_tag_col:
            temp = df.loc[df['tag_id'] == i]
            list_t1 = list(temp['end'])
            list_t2 = list(temp['start'])
            duration = []    
            zip_object = zip(list_t1, list_t2)
            for list1_i, list2_i in zip_object:
                duration.append(list1_i-list2_i)
            max_dur = max(duration)
            x,y,z = positions(temp)
            zip_object_pos = zip(x, y, duration)
            for xi,yi,di in zip_object_pos:
                size = 2
                if di > 2/4*max_dur:
                    size = size*3
                elif di  > 1/4*max_dur:
                    size = size*2
                elif di == 0:
                    size = 1
                plt.plot(xi,yi, color = c, marker='o', markersize = size)
    else:
        temp = df.loc[df['tag_id'] == tag_id]
        list_t1 = list(temp['end'])
        list_t2 = list(temp['start'])
        duration = [] 
        zip_object = zip(list_t1, list_t2)
        for list1_i, list2_i in zip_object:
            duration.append(list1_i-list2_i)
        max_dur = max(duration)
        x,y,z = positions(temp)
        zip_object_pos = zip(x, y, duration)
        for xi,yi,di in zip_object_pos:
            size = 2
            if di > 2/4*max_dur:
                size = size*3
            elif di  > 1/4*max_dur:
                size = size*2 
            elif di == 0:
                size = 1
            plt.plot(xi,yi,'bo--', markersize = size)
     
    plt.show()

# function to plot data from PAA-data    
def plot_cow_PAA(df, tag_id):
    temp = df.loc[df['tag_id'] == tag_id]
    act = list(temp['activity_type'])
    dur = list(temp['duration'])
    dur_cumsum = np.cumsum(dur)
    time = np.zeros(dur_cumsum[-1])
    zip_object = zip(act,dur)
    index = 0
    for a,d in zip_object:
        if a == 998:
           time[index:index+d] = 6
        elif a == 999:
            time[index:index+d] = 7
        else:
            time[index:index+d] = a
            index = index+d       
    plt.plot(time)
    plt.gca().set_yticks([0,1,2,3,4,5,6,7])
    plt.gca().set_yticklabels(['Unknown', 'Standing', 'Walking','In cubicle','At feed', 'At drinker','Out definite','Outside'])
    plt.show()
    
# function to plot distances (with histogram) for PA-data
def plot_distance_PA(df, tag_id1, tag_id2):
    cow_1 = df.loc[df['tag_id'] == tag_id1]
    cow_2 = df.loc[df['tag_id'] == tag_id2]
    x1,y1,z1 = positions(cow_1)
    x2,y2,z2 = positions(cow_2)
    
    times_1_start = list(cow_1['start'])
    times_1_end = list(cow_1['end'])
    times_2_start = list(cow_2['start'])
    times_2_end = list(cow_2['end'])
    
    act_1 = list(cow_1['activity_type'])
    act_2 = list(cow_2['activity_type'])
    
    distance_x = []
    distance_y = []
    
    distance_x.append(x1[0] - x2[0]) # initial distance
    distance_y.append(y1[0] - y2[0])
    i = 0 # index of times_1/x1/y1
    j = 0 # index of times_2/x2/y2
    act = np.ones(len(times_1_start) + len(times_2_start))
    times_comb = []
    times_comb.append(min(times_1_start[0], times_2_start[0]))
    while i < len(times_1_start)-1 or j < len(times_2_start)-1:
        if times_1_start[i] <= times_2_start[j]:           
            if i == len(times_1_start)-1:# if at end of times_1
                j = j+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
            else:
                i = i+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
        else:
            if j == len(times_2_start)-1: # if at end of times_2
                i = i+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
            else:
                j = j+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
        if act_1[i] == 3 or act_2[j] == 3:
            act[i+j] = 0

    distance = []
    temp = times_comb[0]
    times_comb = [x - temp for x in times_comb] # set initial time to zero
    times_comb_plot = [x*1/(3600*1000) for x in times_comb] 

    for i in range(len(distance_x)):
        distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))
    fig, ax =  plt.subplots(2,figsize=(6,6))
    ax[0].plot(times_comb_plot, distance)
    ax[0].set_title('Distance between cow ' + str(tag_id1) + ' and ' + str(tag_id2))
    ax[0].set_xlabel('Time [hours]')
    ax[0].set_ylabel('Distance [cm]')
    #plt.show()
    hist_arr = np.zeros(times_comb[-1])
    index = 0
    for i in range(len(times_comb)-1):
        if act[i] == 1:
            hist_arr[index:times_comb[i+1]] = distance[i]
        else:
            hist_arr[index:times_comb[i+1]] = 0
        index = times_comb[i+1]
    

    hist_arr = [i for i in hist_arr if i != 0]
    ax[1].hist(hist_arr, bins=50)
    ax[1].set_ylabel('#')
    ax[1].set_xlabel('Distance [cm]')
    plt.show()

# function to plot the distance between two cows when within a certain distance
# and when neither of the cows are sleeping
def plot_distance_thres_PA(df, tag_id1, tag_id2, threshold):
    cow_1 = df.loc[df['tag_id'] == tag_id1]
    cow_2 = df.loc[df['tag_id'] == tag_id2]
    x1,y1,z1, act1 = positions_PA(cow_1)
    x2,y2,z2, act2 = positions_PA(cow_2)
    
    times_1_start = list(cow_1['start'])
    times_1_end = list(cow_1['end'])
    times_2_start = list(cow_2['start'])
    times_2_end = list(cow_2['end'])
    
    distance_x = []
    distance_y = []
    
    distance_x.append(x1[0] - x2[0]) # initial distance
    distance_y.append(y1[0] - y2[0])
    i = 0 # index of times_1/x1/y1
    j = 0 # index of times_2/x2/y2
    act = np.ones(len(times_1_start) + len(times_2_start))
    times_comb = []
    times_comb.append(min(times_1_start[0], times_2_start[0]))
    while i < len(times_1_start)-1 or j < len(times_2_start)-1:
        if times_1_start[i] <= times_2_start[j]:           
            if i == len(times_1_start)-1:# if at end of times_1
                j = j+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
            else:
                i = i+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
        else:
            if j == len(times_2_start)-1: # if at end of times_2
                i = i+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
            else:
                j = j+1
                distance_x.append(x1[i] - x2[j]) # new distance
                distance_y.append(y1[i] - y2[j])
                times_comb.append(min(times_2_start[j],times_1_start[i]))
        if act1[i] == 3 or act2[j] == 3:
            act[i+j] = 0

    distance = []
    temp = times_comb[0]
    times_comb = [x - temp for x in times_comb] # set initial time to zero
    times_copy = times_comb.copy()
    times_comb_plot = [x*1/(3600*1000) for x in times_comb] 

    for i in range(len(distance_x)):
        distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))
    
    distance_copy = distance.copy()
    
    for i in range(len(distance_copy)):
        if act[i] == 0:
            distance_copy[i] = np.nan
        elif distance_copy[i] > threshold:
            distance_copy[i] = np.nan

    for i in range(len(times_copy)):
        if np.isnan(distance_copy[i]):
            times_copy[i] = 0
    
        
    fig, ax =  plt.subplots(2,figsize=(6,6))
    ax[0].plot(times_comb_plot, distance_copy, 'go-')
    ax[0].set_title('Distance between cow ' + str(tag_id1) + ' and ' + str(tag_id2))
    ax[0].set_xlabel('Time [hours]')
    ax[0].set_ylabel('Distance [cm]')
    #plt.show()
    hist_arr = np.zeros(times_comb[-1])
    index = 0
    for i in range(len(times_comb)-1):
        if act[i] == 1:
            hist_arr[index:times_comb[i+1]] = distance_copy[i]
        else:
            hist_arr[index:times_comb[i+1]] = 0
        index = times_comb[i+1]
    

    hist_arr = [i for i in hist_arr if i != 0]
    ax[1].hist(hist_arr, bins=50)
    ax[1].set_xlabel('Distance [cm]')
    ax[1].set_ylabel('#')
    plt.show()


###############################################################################
####                               METRICS                                 ####
###############################################################################

# function to get matrix of average distances between cows
def get_distance(df, tag_id):
    res = np.zeros((len(tag_id),len(tag_id)))
    for k in range(len(tag_id)-1):
        for l in range(k+1, len(tag_id)):
            cow_1 = df.loc[df['tag_id'] == tag_id[k]]
            cow_2 = df.loc[df['tag_id'] == tag_id[l]]
            if cow_1.empty == False and cow_2.empty == False:
                x1,y1,z1 = positions(cow_1)
                x2,y2,z2 = positions(cow_2)
                
                times_1 = list(cow_1['time'])
                times_2 = list(cow_2['time'])
                
                distance_x = []
                distance_y = []
                
                distance_x.append(x1[0] - x2[0]) # initial distance
                distance_y.append(y1[0] - y2[0])
                i = 0 # index of times_1/x1/y1
                j = 0 # index of times_2/x2/y2
                times_comb = []
                times_comb.append(min(times_1[0], times_2[0]))
                while i < len(times_1)-1 or j < len(times_2)-1:
                    if times_1[i] <= times_2[j]:           
                        if i == len(times_1)-1:# if at end of times_1
                            j = j+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(times_2[j])
                        else:
                            i = i+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(times_1[i])
                    else:
                        if j == len(times_2)-1: # if at end of times_2
                            i = i+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(times_1[i])
                        else:
                            j = j+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(times_2[j])
            
                distance = []
                temp = times_comb[0]
                times_comb = [x - temp for x in times_comb] # set initial time to zero
                for i in range(len(distance_x)):
                    distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))

                res[k][l] = sum(distance)/len(distance)
    res_df = pd.DataFrame(data=res[0:,0:],index=tag_id, columns=tag_id)  # 1st row as the column names
    return res_df+res_df.T
   
# function same as get_distance() but for PA-data
# histogram not based on distances when either of the cows are sleeping/in cubicle
def get_distance_PA(df, tag_id):
    res_mean = np.zeros((len(tag_id),len(tag_id)))
    res_min = np.zeros((len(tag_id),len(tag_id)))
    for k in range(len(tag_id)-1):
        for l in range(k+1, len(tag_id)):
            cow_1 = df.loc[df['tag_id'] == tag_id[k]]
            cow_2 = df.loc[df['tag_id'] == tag_id[l]]
            if cow_1.empty == False and cow_2.empty == False:
                x1,y1,z1,act_1 = positions_PA(cow_1)
                x2,y2,z2,act_2 = positions_PA(cow_2)
                
                times_1_start = list(cow_1['start'])
                times_1_end = list(cow_1['end'])
                times_2_start = list(cow_2['start'])
                times_2_end = list(cow_2['end'])
                               
                distance_x = []
                distance_y = []
                
                distance_x.append(x1[0] - x2[0]) # initial distance
                distance_y.append(y1[0] - y2[0])
                i = 0 # index of times_1/x1/y1
                j = 0 # index of times_2/x2/y2
                act = np.ones(len(times_1_start) + len(times_2_start))
                times_comb = []
                times_comb.append(min(times_1_start[0], times_2_start[0]))
                while i < len(times_1_start)-1 or j < len(times_2_start)-1:
                    if times_1_start[i] <= times_2_start[j]:           
                        if i == len(times_1_start)-1:# if at end of times_1
                            j = j+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                        else:
                            i = i+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                    else:
                        if j == len(times_2_start)-1: # if at end of times_2
                            i = i+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                        else:
                            j = j+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                    if act_1[i] == 3 or act_2[j] == 3:
                        act[i+j] = 0
            
                distance = []
                temp = times_comb[0]
                times_comb = [x - temp for x in times_comb] # set initial time to zero
                for i in range(len(distance_x)):
                    if act[i] > 0:
                        distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))

                res_mean[k][l] = sum(distance)/len(distance) # average distance
                res_min[k][l] = min(distance) # minimum distance
    res_mean[np.tril_indices(res_mean.shape[0])] = np.nan
    res_min[np.tril_indices(res_min.shape[0])] = np.nan
    res_df_mean = pd.DataFrame(data=res_mean[0:,0:],index=tag_id, columns=tag_id)  # 1st row as the column names
    res_df_min = pd.DataFrame(data=res_min[0:,0:],index=tag_id, columns=tag_id)  
    return res_df_mean, res_df_min

# function to generate matrix of total time when cows are performing different activities 
def diff_act_PA(df, tag_id):
    res = np.zeros((len(tag_id),len(tag_id)))
    for k in range(len(tag_id)-1):
        for l in range(k+1, len(tag_id)):
            cow_1 = df.loc[df['tag_id'] == tag_id[k]]
            cow_2 = df.loc[df['tag_id'] == tag_id[l]]
            if cow_1.empty == False and cow_2.empty == False:
                x1,y1,z1,act_1 = positions_PA(cow_1)
                x2,y2,z2,act_2 = positions_PA(cow_2)
                
                times_1_start = list(cow_1['start'])
                times_1_end = list(cow_1['end'])
                times_2_start = list(cow_2['start'])
                times_2_end = list(cow_2['end'])
                
                i = 0 # index of times_1/x1/y1
                j = 0 # index of times_2/x2/y2
                act = 0
                time_idx = 0
                times_comb = []
                times_comb.append(min(times_1_start[0], times_2_start[0]))
                while i < len(times_1_start)-1 or j < len(times_2_start)-1:
                    if times_1_start[i] <= times_2_start[j]:           
                        if i == len(times_1_start)-1:# if at end of times_1
                            j = j+1
                            time_idx = time_idx + 1
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                        else:
                            i = i+1
                            time_idx = time_idx + 1
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                    else:
                        if j == len(times_2_start)-1: # if at end of times_2
                            i = i+1
                            time_idx = time_idx + 1
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                        else:
                            j = j+1
                            time_idx = time_idx + 1
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                    if act_1[i] != 3 and act_2[j] != 3: # if neither is in cubicle
                        if act_1[i] != act_2[j]:
                            act = act +  times_comb[time_idx] - times_comb[time_idx-1]
                        
                res[k][l] = act/(1000*60) # in minutes
    res[np.tril_indices(res.shape[0])] = np.nan
    res_df = pd.DataFrame(data=res[0:,0:],index=tag_id, columns=tag_id)  # 1st row as the column names
    return res_df

def time_at_feed(df):
    u_cows = unique_cows(df)
    feed_time = [0]*len(u_cows)
    for i in range(len(u_cows)):  # For each cow that has activity type "At feed"
        temp = df.loc[df['tag_id'] == u_cows[i]]
        temp = temp.loc[temp['activity_type'] == 4]

        for index, row in temp.iterrows():
            feed_time[i] += (row['end'] - row['start'])/1000
    return u_cows, feed_time

# function to generate matrix with time spent close to each other
def interaction_time(df, tag_id, dist):
    res = np.zeros((len(tag_id),len(tag_id)))
    for k in range(len(tag_id)-1):
        for l in range(k+1, len(tag_id)):
            cow_1 = df.loc[df['tag_id'] == tag_id[k]]
            cow_2 = df.loc[df['tag_id'] == tag_id[l]]
            if cow_1.empty == False and cow_2.empty == False:
                x1,y1,z1,act_1 = positions_PA(cow_1)
                x2,y2,z2,act_2 = positions_PA(cow_2)
                
                times_1_start = list(cow_1['start'])
                times_1_end = list(cow_1['end'])
                times_2_start = list(cow_2['start'])
                times_2_end = list(cow_2['end'])
                
                distance_x = []
                distance_y = []
                
                distance_x.append(x1[0] - x2[0]) # initial distance
                distance_y.append(y1[0] - y2[0])
                i = 0 # index of times_1/x1/y1
                j = 0 # index of times_2/x2/y2
                time_close = 0 # time spent close to each other
                act = np.ones(len(times_1_start) + len(times_2_start))
                times_comb = []
                times_comb.append(min(times_1_start[0], times_2_start[0]))
                while i < len(times_1_start)-1 or j < len(times_2_start)-1:
                    if times_1_start[i] <= times_2_start[j]:           
                        if i == len(times_1_start)-1:# if at end of times_1
                            j = j+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                        else:
                            i = i+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                    else:
                        if j == len(times_2_start)-1: # if at end of times_2
                            i = i+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                        else:
                            j = j+1
                            distance_x.append(x1[i] - x2[j]) # new distance
                            distance_y.append(y1[i] - y2[j])
                            times_comb.append(min(times_2_start[j],times_1_start[i]))
                    if act_1[i] == 3 or act_2[j] == 3:
                        act[i+j] = 0
            
                temp = times_comb[0]
                times_comb = [x - temp for x in times_comb] # set initial time to zero
                for i in range(len(distance_x)-1):
                    if act[i] > 0:
                        temp_dist = math.sqrt(distance_x[i]**2 + distance_y[i]**2)
                        if temp_dist <= dist:
                            time_close = time_close + (times_comb[i+1]-times_comb[i]) # add time spent close                             

                res[k][l] = time_close/1000
                
    res[np.tril_indices(res.shape[0])] = np.nan
    res_df = pd.DataFrame(data=res[0:,0:],index=tag_id, columns=tag_id)  # 1st row as the column names
    return res_df

#Function to extract velocity vectors based on PA-data
def vector_analysis(df, tag_id, threshold):
    res_mat = np.zeros((len(tag_id),len(tag_id)))
    for k in range(len(tag_id)-1):
        for l in range(k+1, len(tag_id)):
            cow_1 = df.loc[df['tag_id'] == tag_id[k]]
            cow_2 = df.loc[df['tag_id'] == tag_id[l]]
            x1,y1,z1, act1 = positions_PA(cow_1)
            x2,y2,z2, act2 = positions_PA(cow_2)
            
            times_1_start = list(cow_1['start'])
            times_1_end = list(cow_1['end'])
            times_2_start = list(cow_2['start'])
            times_2_end = list(cow_2['end'])
            
            distance_x = []
            distance_y = []
            
            distance_x.append(x1[0] - x2[0]) # initial distance
            distance_y.append(y1[0] - y2[0])
            i = 0 # index of times_1/x1/y1
            j = 0 # index of times_2/x2/y2
            act = np.ones(len(times_1_start) + len(times_2_start))
            times_comb = []
            times_comb.append(min(times_1_start[0], times_2_start[0]))
            x_prod = np.ones(len(times_1_start) + len(times_2_start))
            
            while i < len(times_1_start)-2 or j < len(times_2_start)-2:
                if times_1_start[i] <= times_2_start[j]:           
                    if i == len(times_1_start)-2:# if at end of times_1
                        j = j+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i + 1] - x1[i], y1[i + 1] - y1[i]])
                        arr2 = np.array([x2[j + 1] - x2[j], y2[j + 1] - y2[j]])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
        
                    else:
                        i = i+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i+1]-x1[i], y1[i+1] - y1[i]])
                        arr2 = np.array([x2[j+1]-x2[j], y2[j+1] - y2[j]])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
        
                else:
                    if j == len(times_2_start)-2: # if at end of times_2
                        i = i+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i + 1] - x1[i], y1[i + 1] - y1[i]])
                        arr2 = np.array([x2[j + 1] - x2[j], y2[j + 1] - y2[j]])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
                    else:
                        j = j+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i + 1] - x1[i], y1[i + 1] - y1[i]])
                        arr2 = np.array([x2[j + 1] - x2[j], y2[j + 1] - y2[j]])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
                if act1[i] == 3 or act2[j] == 3:
                    act[i+j] = 0
        
            distance = []
            
            temp = times_comb[0]
            times_comb = [x - temp for x in times_comb] # set initial time to zero
            times_copy = times_comb.copy()
        
            for i in range(len(distance_x)):
                distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))
            
            distance_copy = distance.copy()
            
            for i in range(len(distance_copy)):
                if act[i] == 0:
                    x_prod[i] = np.nan
                elif distance_copy[i] > threshold or x_prod[i] > 15*180/math.pi:
                    x_prod[i] = np.nan
        
            res = []
            for i in range(len(times_copy)):
                if not np.isnan(x_prod[i]):
                    res.append(times_copy[i])
                    
            res_mat[k][l] = len(res)
                
    res_mat[np.tril_indices(res_mat.shape[0])] = np.nan
    res_df = pd.DataFrame(data=res_mat[0:,0:],index=tag_id, columns=tag_id)  # 1st row as the column names

    return res_df

#Function to extract velocity vectors based on PA-data
def vector_analysis_FA(df, tag_id, threshold, speed_thres): # vector analysis for FA-data (included speed)
    res_mat = np.zeros((len(tag_id),len(tag_id)))
    res_mat_time = np.zeros((len(tag_id),len(tag_id), 100000))
    for k in range(len(tag_id)-1):
        for l in range(k+1, len(tag_id)):
            cow_1 = df.loc[df['tag_id'] == tag_id[k]]
            cow_2 = df.loc[df['tag_id'] == tag_id[l]]
            x1,y1,z1 = positions(cow_1)
            x2,y2,z2 = positions(cow_2)
            
            times_1_start = list(cow_1['time'])
            times_2_start = list(cow_2['time'])
            
            temp_time1 = []
            temp_time2 = []
            
            distance_x = []
            distance_y = []
            speed1 = []
            speed2 = []
            
            distance_x.append(x1[0] - x2[0]) # initial distance
            distance_y.append(y1[0] - y2[0])
            arr1 = np.array([x1[1] - x1[0], y1[1] - y1[0]])
            arr2 = np.array([x2[1] - x2[0], y2[1] - y2[0]])
            speed1.append(math.sqrt(arr1[0]**2 + arr1[1]**2)/(times_1_start[1] - times_1_start[0]))
            speed2.append(math.sqrt(arr2[0]**2 + arr2[1]**2)/(times_2_start[1] - times_2_start[0]))
            i = 0 # index of times_1/x1/y1
            j = 0 # index of times_2/x2/y2

            times_comb = []
            times_comb.append(min(times_1_start[0], times_2_start[0]))
            x_prod = np.ones(len(times_1_start) + len(times_2_start))
            
            while i < len(times_1_start)-2 or j < len(times_2_start)-2:
                if times_1_start[i] <= times_2_start[j]:           
                    if i == len(times_1_start)-2:# if at end of times_1
                        j = j+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i + 1] - x1[i], y1[i + 1] - y1[i]])
                        arr2 = np.array([x2[j + 1] - x2[j], y2[j + 1] - y2[j]])
                        speed1.append(math.sqrt(arr1[0]**2 + arr1[1]**2)/(times_1_start[i+1] - times_1_start[i]))
                        speed2.append(math.sqrt(arr2[0]**2 + arr2[1]**2)/(times_2_start[j+1] - times_2_start[j]))
                        temp_time1.append(times_1_start[i])
                        temp_time2.append(times_2_start[j])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
        
                    else:
                        i = i+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i+1]-x1[i], y1[i+1] - y1[i]])
                        arr2 = np.array([x2[j+1]-x2[j], y2[j+1] - y2[j]])
                        
                        speed1.append(math.sqrt(arr1[0]**2 + arr1[1]**2)/(times_1_start[i+1] - times_1_start[i]))
                        speed2.append(math.sqrt(arr2[0]**2 + arr2[1]**2)/(times_2_start[j+1] - times_2_start[j]))
                        temp_time1.append(times_1_start[i])
                        temp_time2.append(times_2_start[j])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
        
                else:
                    if j == len(times_2_start)-2: # if at end of times_2
                        i = i+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i + 1] - x1[i], y1[i + 1] - y1[i]])
                        arr2 = np.array([x2[j + 1] - x2[j], y2[j + 1] - y2[j]])
                        
                        speed1.append(math.sqrt(arr1[0]**2 + arr1[1]**2)/(times_1_start[i+1] - times_1_start[i]))
                        speed2.append(math.sqrt(arr2[0]**2 + arr2[1]**2)/(times_2_start[j+1] - times_2_start[j]))
                        temp_time1.append(times_1_start[i])
                        temp_time2.append(times_2_start[j])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
                    else:
                        j = j+1
                        distance_x.append(x1[i] - x2[j]) # new distance
                        distance_y.append(y1[i] - y2[j])
                        times_comb.append(min(times_2_start[j],times_1_start[i]))
                        arr1 = np.array([x1[i + 1] - x1[i], y1[i + 1] - y1[i]])
                        arr2 = np.array([x2[j + 1] - x2[j], y2[j + 1] - y2[j]])
                        
                        speed1.append(math.sqrt(arr1[0]**2 + arr1[1]**2)/(times_1_start[i+1] - times_1_start[i]))
                        speed2.append(math.sqrt(arr2[0]**2 + arr2[1]**2)/(times_2_start[j+1] - times_2_start[j]))
                        temp_time1.append(times_1_start[i])
                        temp_time2.append(times_2_start[j])
        
                        norm1 = np.linalg.norm(arr1)
                        norm2 = np.linalg.norm(arr2)
        
                        if norm1 != 0 and norm2 != 0:
                            arr1 = arr1 / np.linalg.norm(arr1)
                            arr2 = arr2 / np.linalg.norm(arr2)
        
                            temp_x = np.cross(arr1, arr2)
                            if temp_x>1:
                                temp_x = 1
                            x_prod[i + j] = np.arcsin(temp_x)
                        else:
                            x_prod[i + j] = np.nan
        
            distance = []
            res_time = []
            check_time = 0
            
            temp = times_comb[0]
            times_comb = [x - temp for x in times_comb] # set initial time to zero
            times_copy = times_comb.copy()
        
            for i in range(len(distance_x)):
                distance.append(math.sqrt(distance_x[i]**2 + distance_y[i]**2))
            
            distance_copy = distance.copy()
            
            for i in range(len(distance_copy)):
                if distance_copy[i] > threshold or x_prod[i] > 15*180/math.pi: # within 14 degrees
                    x_prod[i] = np.nan
                elif speed1[i] > speed_thres:
                    x_prod[i] = np.nan
                elif speed2[i] > speed_thres:
                    x_prod[i] = np.nan
                else:
                   res_time.append(min(temp_time1[i], temp_time2[i]))
                   check_time += 1
        
            res = []
            for i in range(len(times_copy)):
                if not np.isnan(x_prod[i]):
                    res.append(times_copy[i])
            if check_time > 0:
                if check_time > 1:
                    for i in range(len(res_time)):
                        res_mat_time[k][l][i] = res_time[i]
                else:
                    res_mat_time[i] = res_time
            res_mat[k][l] = len(res)
                
    res_mat[np.tril_indices(res_mat.shape[0])] = np.nan
    res_df = pd.DataFrame(data=res_mat[0:,0:],index=tag_id, columns=tag_id)  # 1st row as the column names
    
    temp_shape = res_mat_time.shape
    new = res_mat_time.reshape(-1,temp_shape[2], order = "C")

    time_thresh = 10*1000
    temp_shape = new.shape
    result = np.zeros(temp_shape)
    result_count = np.zeros(temp_shape)

    for i in range(len(new[:, 0])):
        temp = new[i, :]
        temp = temp[temp != 0]
        if temp.shape != (0,):
            result_vector = []
            counter = 1
            count_vector =[]
            for j in range(len(temp)-1, 1, -1):
                if not temp[j]-temp[j-1] < time_thresh:
                    count_vector.append(counter)
                    counter = 1
                    result_vector.append(temp[j])
                else:
                    counter +=1
            result_vector.append(temp[0])
            count_vector.append(counter)            
            result[i, 0:len(result_vector)] = result_vector
            result_count[i, 0:len(count_vector)] = count_vector
        else:
            print("EMPTY")

    new = result

    col1 = []
    col2 = []
    for i in range(len(tag_id)):
        temp = [tag_id[i]]
        temp = temp*(len(tag_id))
        col1.extend(temp)
        for j in range(len(tag_id)):
            col2.append(tag_id[j])
  
    col1 = np.transpose(np.asarray(col1))
    col2 = np.transpose(np.asarray(col2))
    result_count = np.insert(result_count, 0, col2, axis=1)
    result_count = np.insert(result_count, 0, col1, axis=1)
    new = np.insert(new, 0, col2, axis=1)
    new = np.insert(new, 0, col1, axis=1)
                
    return res_df, new, result_count


# function to get intersection between two dataframes
def intersect(df1, df2):
    
    df1_tags1 = list(df1.index.get_level_values(level=0))
    df1_tags2 = list(df1.index.get_level_values(level=1))
    list_1 = np.array((df1_tags1,df1_tags2)).transpose()
    
    df2_tags1 = list(df2.index.get_level_values(level=0))
    df2_tags2 = list(df2.index.get_level_values(level=1))
    list_2 = np.array((df2_tags1,df2_tags2)).transpose()
        
    res = np.zeros(shape=(len(df1_tags1),2))

    idx = 0
    for i in range(len(df1_tags1)):
        if any((list_1[:]==list_2[i]).all(1)):
            res[idx] = list_2[i]
            idx = idx + 1
    
    res = res[~np.all(res == 0, axis=1)]
    return res

#Function to produce displacement textfiles
def displacement(df_PA, u_cows, tag_id, textfile = 'result.txt'):
    cow = df_PA.loc[df_PA['tag_id'] == tag_id]
    x, y, z, act = positions_PA(cow)

    indices = [i for i, x in enumerate(act) if x == 4]

    cow = cow.iloc[indices]

    start = list(cow['start'])
    end = list(cow['end'])
    x, y, z, act= positions_PA(cow)

    res_time = []
    res_pos = []
    for i in range(len(indices)-1):
        if  5*1000 < start[i+1] - end[i] < 30*1000 and y[i]>3000 and 100<abs(y[i]-y[i+1]): #and end[i]-start[i]>10*1000:
            res_time.append(end[i])
            res_pos.append((x[i], y[i]))

    #print(tag_id)
    #print(res_time)
    with open(textfile, "a") as file:
        file.write("Original cow: " + str(tag_id) + "\n")
        print("Original cow: " + str(tag_id))
    
        for i in range(len(res_time)):
    
            hostile_cows = []
            for cow in u_cows:
                if cow != tag_id:
                    cow_subset = df_PA.loc[df_PA['tag_id'] == cow]
                    for index, row in cow_subset.iterrows():
                        if 0 < res_time[i]-row['start']<5*1000 and 100 >(math.sqrt(math.pow(row['x']-res_pos[i][0], 2) + math.pow(row['y']-res_pos[i][1], 2))):
                            hostile_cows.append(cow)
            if len(hostile_cows)!= 0:
                file.write(str(res_time[i]))
                file.write((str(hostile_cows)))
                file.write("\n")
                print(res_time[i])
                print(hostile_cows)
    #file.close()




###############################################################################
####                              ANIMATION                                ####
###############################################################################
pause = False

def animate_cowsV2(df, cowID_1, cowID_2, barn_filename, interesting_time, save_path='n'):

    f, ax1 = plot_barnV2(barn_filename) #Get barn koordinates

    ax1, nearby_cows = plot_all_cows(ax1, df, interesting_time, [cowID_1, cowID_2]) #Get all records of gray cows

    unimportant_cows = nearby_cows.copy()

    nearby_cows.append(cowID_1) #Ad interesting cows
    nearby_cows.append(cowID_2)


    df_cows = df[df['tag_id'].isin(nearby_cows)]

    df_cows = df_cows.sort_values('time')

    x, y, z = positions(df_cows)

    tag_id = list(df_cows['tag_id'])

    time = list(df_cows['time'])

    timestrings = []

    #This counts how many times the ineresting cows move and base the number of frames presented on this
    frames = 0
    for tag in tag_id:
        if tag == cowID_1 or tag == cowID_2:
            frames +=1

    #This makes the timestrings that is printed and adjust them for timezone and daylight savings
    for timestamp in time:
        timestrings.append(datetime.fromtimestamp((timestamp/1000)-7200))

    ax1.change_geometry(2, 1, 1)
    ax2 = f.add_subplot(212)
    ax1.set_aspect('equal', 'datalim')


    plt.tight_layout()

    pos1 = ax1.get_position().bounds
    pos2 = ax2.get_position().bounds

    new_pos1 = [pos1[0], 0.25, pos1[2], 0.7]
    new_pos2 = [pos2[0], pos2[1], pos2[2], 0.1]
    ax1.set_position(new_pos1)
    ax2.set_position(new_pos2)
    
    
    xdata1, ydata1 = [x[tag_id.index(cowID_1)]], [y[tag_id.index(cowID_1)]]

    xdata2, ydata2 = [x[tag_id.index(cowID_2)]], [y[tag_id.index(cowID_2)]]

    dist, time = [], []

    list_of_dots =[]

    for i in range(len(unimportant_cows)+2):
        if i == len(unimportant_cows):
            list_of_dots.append(ax1.plot([], [], '-', alpha = 0.8)[0])
            list_of_dots.append(ax1.plot([], [], 'co', label='Cow ' + str(cowID_1), alpha = 0.5)[0])
            
        elif i == len(unimportant_cows)+1:
            list_of_dots.append(ax1.plot([], [], '-', alpha = 0.8)[0])
            list_of_dots.append(ax1.plot([], [], 'yo', label='Cow ' + str(cowID_2), alpha = 0.5)[0])
            
        else:
            list_of_dots.append(ax1.plot([], [], 'o', color='tab:gray', alpha = 0.8)[0])

    list_of_dots.append(ax2.plot([], [], 'r-')[0])

    ax1.legend(loc='upper right')

    ax1.set_ylim(0, 3340)
    ax1.set_xlim(0, 8738)
    ax2.set_xlim(timestrings[0], timestrings[len(timestrings) - 1])

    ax2.set_ylim(0, 10000)
    date1 = timestrings[0]
    date2 = timestrings[len(timestrings) - 1]
    ax1.set_title("Plot of two cows between " + date1.strftime("%d %b %Y %H:%M") + " - " +
                  date2.strftime("%d %b %Y %H:%M"), fontsize=8)
    ax2.set_ylabel('Distance(cm)')
    ax2.set_xlabel('Time of day')

    def run_animation(): #If the window is clicked, the animation pauses
        ani_running = True
        i = 0
        def onClick(event):
            nonlocal ani_running
            if ani_running:
                ani.event_source.stop()
                ani_running = False
            else:
                ani.event_source.start()
                ani_running = True


        def update(frame): #Update function for the animation, what happens each frame
            nonlocal i
            if not pause:
                check = 0
                while check == 0:
                    if tag_id[i] == cowID_1:
                        check = 1
                        xdata1.append(x[i])  # new distance
                        ydata1.append(y[i])
                        xdata2.append(xdata2[-1])  # new distance
                        ydata2.append(ydata2[-1])

                    elif tag_id[i] == cowID_2:
                        check = 1
                        xdata2.append(x[i])  # new distance
                        ydata2.append(y[i])
                        xdata1.append(xdata1[-1])  # new distance
                        ydata1.append(ydata1[-1])

                    else:
                        index = unimportant_cows.index(tag_id[i])
                        list_of_dots[index].set_data(y[i], x[i])

                    i += 1

                list_of_dots[-5].set_data(ydata1, xdata1)
                list_of_dots[-4].set_data(ydata1[-1], xdata1[-1])
                list_of_dots[-3].set_data(ydata2, xdata2)
                list_of_dots[-2].set_data(ydata2[-1], xdata2[-1])

                dist.append(math.sqrt(math.pow(xdata1[-1]-xdata2[-1], 2) + math.pow(ydata1[-1]-ydata2[-1], 2)))

                time.append((timestrings[i]))

                list_of_dots[-1].set_data(time, dist)

            return list_of_dots

        f.canvas.mpl_connect('button_press_event', onClick)
        ani = FuncAnimation(f, update, frames=frames, blit=True, interval=50, repeat=False)

        #HAndles saving the animation if filename is given
        if save_path != 'n':
            try:
                ani.save(save_path)
            except:
                print('Wrong filepath')

        plt.show()

    run_animation()








def animate_cows(df, cowID_1, cowID_2, barn_filename, save_path='n'):

    cow_1 = df.loc[df['tag_id'] == cowID_1]

    cow_2 = df.loc[df['tag_id'] == cowID_2]

    x1, y1, z1 = positions(cow_1)
    x2, y2, z2 = positions(cow_2)

    time1 = list(cow_1['time'])
    time2 = list(cow_2['time'])

    timestrings1= []
    timestrings2 = []

    for timestamp1 in time1:
        timestrings1.append(datetime.fromtimestamp((timestamp1/1000)-7200))

    for timestamp2 in time2:
        timestrings2.append(datetime.fromtimestamp((timestamp2 / 1000) - 7200))

    f, ax1 = plot_barn(barn_filename)


    ax1.change_geometry(2, 1, 1)
    ax2 = f.add_subplot(212)

    plt.tight_layout()

    pos1 = ax1.get_position().bounds
    pos2 = ax2.get_position().bounds

    new_pos1 = [pos1[0], 0.25, pos1[2], 0.7]
    new_pos2 = [pos2[0], pos2[1], pos2[2], 0.1]

    ax1.set_position(new_pos1)
    ax2.set_position(new_pos2)

    xdata1, ydata1 = [], []
    ln1, = ax1.plot([], [], '-')
    xdata2, ydata2 = [], []
    ln2, = ax1.plot([], [], '-')

    d1, = ax1.plot([], [], 'co', label='Cow '+ str(cowID_1))
    d2, = ax1.plot([], [], 'yo', label='Cow '+ str(cowID_2))

    ax1.legend(loc='upper left')

    dist, time = [], []
    dist_plot, = ax2.plot([], [], 'r-')

    def run_animation():
        ani_running = True
        i = 0
        j = 0
        def onClick(event): #If the window is clicked, the gif pauses
            nonlocal ani_running
            if ani_running:
                ani.event_source.stop()
                ani_running = False
            else:
                ani.event_source.start()
                ani_running = True

        def init():
            ax1.set_xlim(0, 3340)
            ax1.set_ylim(0, 8738)
            ax2.set_xlim(timestrings1[0], timestrings1[len(timestrings1)-1])

            ax2.set_ylim(0, 10000)
            date1 = timestrings1[0]
            date2 = timestrings1[len(timestrings1)-1]
            ax1.set_title("Plot of two cows between " + date1.strftime("%d %b %Y %H:%M") + " - " +
                          date2.strftime("%d %b %Y %H:%M"), fontsize=8)
            ax2.set_ylabel('Distance(cm)')
            ax2.set_xlabel('Time of day')

            return ln1, ln2, d1, d2, dist_plot

        def update(frame):
            nonlocal i
            nonlocal j
            if not pause:
                if time1[i] <= time2[j]:
                    if i == len(time1) - 1:  # if at end of times_1
                        j = j + 1
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])
                    else:
                        i = i + 1
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                else:
                    if j == len(time2) - 1:  # if at end of times_2
                        i = i + 1
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                    else:
                        j = j + 1
                        xdata2.append(x2[j])  # new distance
                        ydata2.append(y2[j])
                        xdata1.append(x1[i])  # new distance
                        ydata1.append(y1[i])

                ln1.set_data(xdata1, ydata1) #Uppdate the plot with the data
                d1.set_data(x1[i], y1[i])
                ln2.set_data(xdata2, ydata2)
                d2.set_data(x2[j], y2[j])
                dist.append(math.sqrt(math.pow(x1[i]-x2[j], 2) + math.pow(y1[i]-y2[j], 2)))

                if time1[i]<time2[j]: #Uppdate the correct time
                    time.append((timestrings1[i]))
                else:
                    time.append((timestrings2[j]))


                dist_plot.set_data(time, dist)

            return ln1, ln2, d1, d2, dist_plot

        f.canvas.mpl_connect('button_press_event', onClick)
        ani = FuncAnimation(f, update, frames=len(time1)+len(time2)-2, init_func=init, blit=True, interval=1, repeat=False) #Main animationfunction
        if save_path != 'n': #If a filename is given, the gif is saved
            try:
                ani.save(save_path)
            except:
                print('Wrong filepath')

        plt.show()

    run_animation()    
    
###############################################################################
####                           OTHER                                       ####
###############################################################################

# function to extract position data of a dataframe, for PA-data    
def positions_PA(df):
    x = list(df['x'])
    y = list(df['y'])
    z = list(df['z'])
    activity = list(df['activity_type'])
    return x,y,z, activity

# extract position data from dataframe
def positions(df):
    x = list(df['x'])
    y = list(df['y'])
    z = list(df['z'])
    return x,y,z






       

    

