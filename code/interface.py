######################################################################################################
# Author: Yuna Otrante-Chardonnet
# Start: April 27th 2021
# Title: interface.py
# Description: 
# 
#
######################################################################################################

from tkinter import *
import tkcalendar as tkdate
import initialization as init, distance as dist
from pathlib import Path
from progress.bar import Bar
import functions as func
import datetime

def main_frame():

    # Load data file to create dataframe
    def clicked_file(): 
        ### From Torsten and Björn code ###
        lbl_file.config(text="Wait...")
        lbl_file.update_idletasks()
        y = str(cal.get_date().year) # get year, month and day from calendar
        mo = str(cal.get_date().month)
        d = str(cal.get_date().day)
        if len(mo) == 1:
            mo = "0"+mo
        if len(d) == 1:
            d = "0"+d
        
        FA_file = "../data/FA_"+y+mo+d+"T000000UTC.csv"
        ###

        global df
        df = init.csv_read_bis(FA_file) #Test (6 cows)
        #df = init.csv_read(FA_file) # All the cows

        lbl_file.config(text="Data loaded")
        btn_histo.configure(state = NORMAL) 
        btn_all_histo.configure(state = NORMAL)
        # Create folders if not exist to store data
        Path("../data/" + str(cal.get_date()) + '/cows').mkdir(parents=True, exist_ok=True)
        Path("../data/" + str(cal.get_date()) + '/merged data').mkdir(parents=True, exist_ok=True)
        Path("../data/" + str(cal.get_date()) + '/histograms/left').mkdir(parents=True, exist_ok=True)
        Path("../data/" + str(cal.get_date()) + '/histograms/right').mkdir(parents=True, exist_ok=True)

    # Create cow dataframe 
    def compute_cow(path,cow_id,e_min,e_max,area):
        # Check if the cow data has already been computed 
        if Path(path).is_file() or Path(path.replace(area,'all')).is_file():
            # If found file area == all but given area != all
            if Path(path).is_file() != True:
                cow = init.csv_read_cow(path.replace(area,'all'))
                if area.startswith("custom"):
                    cow = init.custom_area(cow,int(entry_x1.get()),int(entry_x2.get()),int(entry_y1.get()),int(entry_y2.get()))
                    cow.to_csv (r''+ path, index = False, header=False)
                else:   
                    cow = init.area_delimitation(cow,area)
                    cow.to_csv (r''+ path, index = False, header=False)
            else:
                cow = init.csv_read_cow(path)
        else:
            cow = init.create_cow(cow_id, df,e_min,e_max,area)
            if area.startswith("custom"):
                cow = init.custom_area(cow,int(entry_x1.get()),int(entry_x2.get()),int(entry_y1.get()),int(entry_y2.get()))
            cow = init.fill_data(cow,area)
            # Save cow data
            cow.to_csv (r''+ path, index = False, header=False)
        return cow

    # Create histogram for a pair of cows
    def get_histogram():
        lbl_file.config(text="Processing...  0/2")
        lbl_file.update_idletasks()
        global df

        # get staring time from the entry
        t_min = datetime.datetime.strptime(entry_time1.get(), '%H:%M').time()
        e_min = int((datetime.datetime(cal.get_date().year,cal.get_date().month,cal.get_date().day,t_min.hour,t_min.minute)- datetime.datetime(1970,1,1)).total_seconds())

        # get ending time from the entry
        t_max = datetime.datetime.strptime(entry_time2.get(), '%H:%M').time()
        e_max = int((datetime.datetime(cal.get_date().year,cal.get_date().month,cal.get_date().day,t_max.hour,t_max.minute) + datetime.timedelta(minutes=1) - datetime.datetime(1970,1,1)).total_seconds())

        area = area_var.get()
        if area == "custom":
            area = "custom_" + str(entry_x1.get()) + '_' + str(entry_x2.get()) + '_' + str(entry_y1.get()) + '_' + str(entry_y2.get())

        c1 = compute_cow('../data/' + str(cal.get_date()) + '/cows' + '/' + str(entry_cow1.get()) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area + '.csv', int(entry_cow1.get()),e_min,e_max,area)

        lbl_file.config(text="Processing...  1/2")
        lbl_file.update_idletasks()

        # if the "both" checkbox is not checked
        if check_area_var.get() == 0:
            area = "all"
        c2 = compute_cow('../data/' + str(cal.get_date()) + '/cows' + '/' + str(entry_cow2.get()) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area + '.csv', int(entry_cow2.get()),e_min,e_max,area)

        lbl_file.config(text="Processing...  2/2")
        lbl_file.update_idletasks()

        res = dist.compare(c1,c2)
        res = dist.compute_distance(res)

        if check_save_var.get() == 1:
            if check_area_var.get() == 1:
                area_check = area + "_both"
            else:
                area_check = area
    
            res.to_csv(r''+ '../data/' + str(cal.get_date()) + '/merged data' + '/merged_' + str(entry_cow1.get()) + '_' + str(entry_cow2.get()) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area_check + '.csv', index = False, header=True)

        lbl_file.config(text="Done")
        dist.histogram(res,1,NONE,int(entry_bar.get()),t_min,t_max)

    # Get histograms for cows on one side of the barn
    def compute_side(list_side,e_min,e_max,t_min,t_max,nb_histo,side,i):
        area = area_var.get()
        if area == "custom":
            area = "custom_" + str(entry_x1.get()) + '_' + str(entry_x2.get()) + '_' + str(entry_y1.get()) + '_' + str(entry_y2.get())
        if check_area_var.get() == 1:
            area_check = area + "_both"
        else:
            area_check = area


        while len(list_side)>0:
            cow_id1 = list_side[0]
            list_side.remove(list_side[0])
            c1 = compute_cow('../data/' + str(cal.get_date()) + '/cows' + '/' + str(cow_id1) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area + '.csv', cow_id1,e_min,e_max,area)

            for cow_id2 in list_side:
                if check_area_var.get() == 0:
                    c2 = compute_cow('../data/' + str(cal.get_date()) + '/cows' + '/' + str(cow_id2) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_all.csv', cow_id2,e_min,e_max,'all')
                else:
                    c2 = compute_cow('../data/' + str(cal.get_date()) + '/cows' + '/' + str(cow_id2) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area + '.csv', cow_id2,e_min,e_max,area)

                res = dist.compare(c1,c2)
                res = dist.compute_distance(res)
                if check_save_var.get() == 1:
                    res.to_csv(r''+ '../data/' + str(cal.get_date()) + '/merged data/merged_' + str(cow_id1) + '_' + str(cow_id2) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area_check + '.csv', index = False, header=True)
                dist.histogram(res,0,'../data/' + str(cal.get_date()) + '/histograms/' + side + '/' + str(cow_id1) + '_' + str(cow_id2) + '_' + t_min.strftime("%H%M") + '_' + t_max.strftime("%H%M") + '_' + area_check + '.png',int(entry_bar.get()),t_min,t_max)

                lbl_file.config(text="Processing...  " + str(i) + '/' + str(nb_histo))
                lbl_file.update_idletasks()
                i+=1
        return i


    def get_all_histograms():
        global df

        # get staring time from the entry
        t_min = datetime.datetime.strptime(entry_time1.get(), '%H:%M').time()
        e_min = int((datetime.datetime(cal.get_date().year,cal.get_date().month,cal.get_date().day,t_min.hour,t_min.minute)- datetime.datetime(1970,1,1)).total_seconds())

        # get ending time from the entry
        t_max = datetime.datetime.strptime(entry_time2.get(), '%H:%M').time()
        e_max = int((datetime.datetime(cal.get_date().year,cal.get_date().month,cal.get_date().day,t_max.hour,t_max.minute) + datetime.timedelta(minutes=1) - datetime.datetime(1970,1,1)).total_seconds())

        # Separate left cows and right cows
        df_left, df_right = func.left_right(df, '../data/barn.csv')
        list_cow_left = df_left.tag_id.unique().tolist()
        list_cow_right = df_right.tag_id.unique().tolist()

        nb_cows_left = len(list_cow_left)
        nb_cows_right = len(list_cow_right)
        nb_histo = 0

        # determind the number of histogram to print it
        if nb_cows_left:
            for i in range (1,nb_cows_left):
                nb_histo += i
        if nb_cows_right:
            for i in range (1,nb_cows_right):
                nb_histo += i

        i = 0
        i = compute_side(list_cow_left,e_min,e_max,t_min,t_max,nb_histo,"left",i)
        i = compute_side(list_cow_right,e_min,e_max,t_min,t_max,nb_histo,"right",i)
        
        lbl_file.config(text="Done")

    # Quit the interface
    def quit_me():
        print('quit')
        window.quit()
        window.destroy()

    # Set number of bars to 50 
    def defaul_nb_bar():
        entry_bar.delete(0,'end')
        entry_bar.insert(0, "50")

    # Display entries to enter the coordinates or hide them
    def is_custom(value):
        if value == 'custom':
            lbl_x1.place(relx = 0.35, rely = 0.39)
            entry_x1.place(relx = 0.40, rely = 0.39)
            lbl_x2.place(relx = 0.50, rely = 0.39)
            entry_x2.place(relx = 0.55, rely = 0.39)
            lbl_y1.place(relx = 0.65, rely = 0.39)
            entry_y1.place(relx = 0.70, rely = 0.39)
            lbl_y2.place(relx = 0.80, rely = 0.39)
            entry_y2.place(relx = 0.85, rely = 0.39)

        else:   
            lbl_x1.place_forget()
            entry_x1.place_forget()
            lbl_x2.place_forget()
            entry_x2.place_forget()
            lbl_y1.place_forget()
            entry_y1.place_forget()
            lbl_y2.place_forget()
            entry_y2.place_forget()

    window = Tk()
    window.title("Cow histogram")
    window.geometry("600x400")
    window.configure(bg='white')
    window.protocol("WM_DELETE_WINDOW", quit_me)

    header = Label(window,text = "Histogram of the distance between two peers in 24h", bg='white')
    header.place(relx = 0.5, rely = 0.1, anchor = CENTER)

    lbl_cal = Label(window,text = "Select date: ", bg='white')
    lbl_cal.place(relx = 0.1, rely = 0.2)

    cal = tkdate.DateEntry(window)
    cal.place(relx = 0.4, rely = 0.2)

    btn_file = Button(window, state = NORMAL, text = "Load data from file", bg='white', command = clicked_file)
    btn_file.place(relx = 0.7, rely = 0.19)

    lbl_time1 = Label(window,text = "From:", bg='white')
    lbl_time1.place(relx = 0.1, rely = 0.3)

    entry_time1 = Entry(window,bg='#F3F3F3',width=7,justify='center')
    entry_time1.place(relx = 0.17, rely = 0.3)
    entry_time1.insert(0, "00:00")

    lbl_time2 = Label(window,text = "to:", bg='white')
    lbl_time2.place(relx = 0.25, rely = 0.3)

    entry_time2 = Entry(window,bg='#F3F3F3',width=7,justify='center')
    entry_time2.place(relx = 0.30, rely = 0.3)
    entry_time2.insert(0, "23:59")

    lbl_bar = Label(window,text = "Nb of bars:", bg='white')
    lbl_bar.place(relx = 0.6, rely = 0.3)

    entry_bar = Entry(window,bg='#F3F3F3',width=7,justify='center')
    entry_bar.place(relx = 0.71, rely = 0.3)
    entry_bar.insert(0, "50")

    btn_bar = Button(window, state = NORMAL, text = "Default", bg='white', command = defaul_nb_bar)
    btn_bar.place(relx = 0.8, rely = 0.3)
    
    lbl_area = Label(window,text = "Area:", bg='white')
    lbl_area.place(relx = 0.1, rely = 0.4)

    area_var = StringVar(window)
    area_var.set("all")
    menu_area = OptionMenu(window, area_var, "all", "feeding", "bedding", "cubicle", "alley", "custom", command= is_custom)
    menu_area.place(relx = 0.17, rely = 0.39)

    lbl_x1 = Label(window,text = "X1:", bg='white')
    entry_x1 = Entry(window,bg='#F3F3F3',width=7,justify='center')
    lbl_x2 = Label(window,text = "X2:", bg='white')
    entry_x2 = Entry(window,bg='#F3F3F3',width=7,justify='center')
    lbl_y1 = Label(window,text = "Y1:", bg='white')
    entry_y1 = Entry(window,bg='#F3F3F3',width=7,justify='center')
    lbl_y2 = Label(window,text = "Y2:", bg='white')
    entry_y2 = Entry(window,bg='#F3F3F3',width=7,justify='center')

    check_area_var = IntVar()
    check_area = Checkbutton(window, text="Both in the area", variable=check_area_var, onvalue=1, offvalue=0, bg='white')
    check_area.place(relx = 0.1, rely = 0.48)

    check_save_var = IntVar()
    check_save = Checkbutton(window, text="Save the merged data", variable=check_save_var, onvalue=1, offvalue=0, bg='white')
    check_save.place(relx = 0.6, rely = 0.48)

    lbl_cow1 = Label(window,text = "Cow ID 1:", bg='white')
    lbl_cow1.place(relx = 0.1, rely = 0.6)

    entry_cow1 = Entry(window,bg='#F3F3F3',width=18)
    entry_cow1.place(relx = 0.2, rely = 0.6)

    lbl_cow2 = Label(window,text = "Cow ID 2:", bg='white')
    lbl_cow2.place(relx = 0.6, rely = 0.6)

    entry_cow2 = Entry(window,bg='#F3F3F3',width=18)
    entry_cow2.place(relx = 0.7, rely = 0.6)

    btn_histo = Button(window, state = DISABLED, text = "Get histogram", bg='white', command = get_histogram)
    btn_histo.place(relx = 0.3, rely = 0.75)

    btn_all_histo = Button(window, state = DISABLED, text = "Get all histograms", bg='white', command = get_all_histograms)
    btn_all_histo.place(relx = 0.6, rely = 0.75)

    lbl_file = Label(window,text = "", bg='white')
    lbl_file.place(relx = 0.45, rely = 0.85)
            
    window.mainloop()