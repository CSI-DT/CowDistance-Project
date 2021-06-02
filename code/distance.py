######################################################################################################
# Author: Yuna Otrante-Chardonnet
# Start: April 27th 2021
# Title: distance.py
# Description: 
# 
#
######################################################################################################

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Compare 2 cows and return the merged dataframe when the rows match (on rounded time)
def compare(df_cow1, df_cow2):
    return pd.merge(df_cow1, df_cow2, how="inner", on="rounded_time")

# Get the distance between two cows for each row
def compute_distance(df):
    df['distance'] = ((df['x_y'] - df['x_x'])**2 + (df['y_y'] - df['y_x'])**2).apply(np.sqrt)
    return df

def histogram(df,show,path,nb_bar,t_min,t_max):
    if df.empty is False:
        df.hist(column='distance',bins=nb_bar)
        c1 = str(df['tag_id_x'].loc[0])
        c2 = str(df['tag_id_y'].loc[0])
        title = "Distance " + c1 + " and " + c2 + " between " + t_min.strftime("%H:%M") + " and " + t_max.strftime("%H:%M")
        plt.title(title)
        plt.xlabel("Distance (in cm)")
        if show == 1:
            plt.show()
        if show == 0:
            plt.savefig(path)
        plt.close()