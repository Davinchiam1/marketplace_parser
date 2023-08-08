import time
import tkinter as tk
import os
import calendar
import threading
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from tkcalendar import DateEntry
import parser_amazon
import patser_wb
import hel10_sales_download as h10
from gl_trends_req import Common_trends

from datetime import datetime


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Main window with load from api and load from files blocks"""

        # asin/key or path to asins/keys file
        self.asin_label = tk.Label(self, text="ASIN/KEY:")
        self.asin_label.grid(row=0, column=0, sticky=tk.W)
        self.asin_entry = tk.Entry(self)
        self.asin_entry.grid(row=0, column=1)
        self.asin_button = tk.Button(self, text="Browse ASIN/KEY file...", command=self.browse_asin_file)
        self.asin_button.grid(row=0, column=2)

        # choose marketpace
        self.az_wb_var = tk.StringVar()
        self.az_wb_var.set("az")
        self.rb01 = tk.Radiobutton(self, text="Wildberries", variable=self.az_wb_var, value="wb")
        self.rb02 = tk.Radiobutton(self, text="Amazon", variable=self.az_wb_var, value="az")
        self.rb01.grid(row=1, column=1, sticky=tk.N)
        self.rb02.grid(row=1, column=0, sticky=tk.N)

        # choose end date for loading period
        self.date_label = tk.Label(self, text="Load up to:")
        self.date_label.grid(row=2, column=0, columnspan=3, sticky=tk.N)

        # day enter
        self.last_day = tk.Label(self, text="Day:")
        self.last_day.grid(row=4, column=0, sticky=tk.W)
        self.last_day_entry = tk.Entry(self)
        self.last_day_entry.grid(row=3, column=0)

        # mouth enter
        self.last_mounth = tk.Label(self, text="Mounth:")
        self.last_mounth.grid(row=4, column=1, sticky=tk.W)
        self.last_mounth_entry = tk.Entry(self)
        self.last_mounth_entry.grid(row=3, column=1)

        # year enter
        self.last_year = tk.Label(self, text="Year:")
        self.last_year.grid(row=4, column=2, sticky=tk.W)
        self.last_year_entry = tk.Entry(self)
        self.last_year_entry.grid(row=3, column=2)

        # category enter (for file name)
        self.cat_label = tk.Label(self, text="Category name:")
        self.cat_label.grid(row=5, column=0, sticky=tk.W)
        self.cat_entry = tk.Entry(self)
        self.cat_entry.grid(row=5, column=1)

        # save directory path
        self.save_label = tk.Label(self, text="Save directory:")
        self.save_label.grid(row=6, column=0, sticky=tk.W)
        self.save_entry = tk.Entry(self)
        self.save_entry.grid(row=6, column=1)
        self.save_button = tk.Button(self, text="Browse...", command=self.browse_save_directory)
        self.save_button.grid(row=6, column=2)

        # button for load feedbacks
        self.load_button = tk.Button(self, text="Load feedbacks...", command=self.load_feedbacks)
        self.load_button.grid(row=7, column=0)

        # load sales
        self.load_sales_button = tk.Button(self, text="Load sales...", command=self.load_sales)
        self.load_sales_button.grid(row=7, column=1)

        # button for human interaction(chapcha and ect.)
        self.human_interraction = tk.Button(self, text="Ready!", command=self.human_ready)
        self.human_interraction.grid(row=7, column=2)

        # load searches
        self.load_search_button = tk.Button(self, text="Load searches...", command=self.load_searches)
        self.load_search_button.grid(row=7, column=3)

        # button for opening new window for google trends
        self.new_window_button = tk.Button(self, text="Google Trends", command=self.open_new_window)
        self.new_window_button.grid(row=6, column=3)

    def open_new_window(self):
        """Secondary window for loading trends from google trends"""
        new_window = tk.Toplevel(self.master)
        new_window.title("Google trends")
        new_window.geometry("350x150")

        # keys entering or path to keywords file
        self.asin_label  = tk.Label(new_window, text="KEYS:")
        self.asin_label .grid(row=0, column=0, sticky=tk.W)
        self.asin_entry = tk.Entry(new_window)
        self.asin_entry.grid(row=0, column=1)
        self.asin_button = tk.Button(new_window, text="Browse...", command=self.browse_asin_file)
        self.asin_button.grid(row=0, column=2)

        # enter field for region (two-letter designation)
        self.region = tk.Label(new_window, text="Region:")
        self.region.grid(row=1, column=0, sticky=tk.W)
        self.region_entry = tk.Entry(new_window)
        self.region_entry.grid(row=1, column=1)

        # set of options to choose

        #  to load info about searches in region (country)
        self.get_region_var = tk.BooleanVar()
        self.get_region_checkbox = tk.Checkbutton(new_window, text="Keys in region", variable=self.get_region_var)
        self.get_region_checkbox.grid(row=2, column=0, sticky=tk.W)

        # to load global info about keys divided by country
        self.get_global_var = tk.BooleanVar()
        self.get_global_checkbox = tk.Checkbutton(new_window, text="Keys by country", variable=self.get_global_var)
        self.get_global_checkbox.grid(row=2, column=1, sticky=tk.W)

        # to load info about keys in country divided by subregions(City and ect.)
        self.get_by_country_var = tk.BooleanVar()
        self.get_by_country_checkbox = tk.Checkbutton(new_window, text="Keys by subregion",
                                                      variable=self.get_by_country_var)
        self.get_by_country_checkbox.grid(row=2, column=2, sticky=tk.W)

        # to load topics related to keys
        self.related_topics_var = tk.BooleanVar()
        self.related_topics_checkbox = tk.Checkbutton(new_window, text="Related topics",
                                                      variable=self.related_topics_var)
        self.related_topics_checkbox.grid(row=3, column=0, sticky=tk.W)

        # to load related searches for keys
        self.related_searches_var = tk.BooleanVar()
        self.related_searches_checkbox = tk.Checkbutton(new_window, text="Related searches",
                                                        variable=self.related_searches_var)
        self.related_searches_checkbox.grid(row=3, column=1, sticky=tk.W)

        # to load suggested topics for keys
        self.suggested_topics_var = tk.BooleanVar()
        self.suggested_topics_checkbox = tk.Checkbutton(new_window, text="Suggested topics",
                                                        variable=self.suggested_topics_var)
        self.suggested_topics_checkbox.grid(row=3, column=2, sticky=tk.W)

        # to load filepath fo saving result files
        self.save_label = tk.Label(new_window, text="Save directory:")
        self.save_label.grid(row=4, column=0, sticky=tk.W)
        self.save_entry = tk.Entry(new_window)
        self.save_entry.grid(row=4, column=1)
        self.save_button = tk.Button(new_window, text="Browse...", command=self.browse_save_directory)
        self.save_button.grid(row=4, column=2)

        # start loading chosen features
        self.load_trends_button = tk.Button(new_window, text="Load Trends", command=self.load_trends)
        self.load_trends_button.grid(row=5, column=1, sticky=tk.S)

    def update_human_button_state(self):
        if h10.human_inter:  # Condition for enabling/disabling the button
            self.human_interraction.config(state=tk.NORMAL)  # Enable button
        else:
            self.human_interraction.config(state=tk.DISABLED)  # Выключить кнопку
    def load_sales_thread(self):
        threading.Thread(target=self.load_sales).start()

    def load_searches_thread(self):
        threading.Thread(target=self.load_searches).start()

    def browse_save_directory(self):
        """Get dir to save loaded files"""
        save_directory = filedialog.askdirectory()
        self.save_entry.delete(0, tk.END)
        self.save_entry.insert(0, save_directory)

    def browse_asin_file(self):
        """Get asin from file"""
        filetypes = [("CSV files", "*.csv"), ("XLSX files", "*.xlsx")]
        directory = filedialog.askopenfilenames(initialdir=".", filetypes=filetypes)
        if isinstance(directory, tuple):  # Checking if result is a tuple (for prevent bugs in some systems)
            directory = directory[0]
        self.asin_entry.delete(0, tk.END)
        self.asin_entry.insert(0, directory)


    def load_feedbacks(self):
        """Get reviews for provided products (by asin for AZ or by sku for WB) up to provided date"""
        asin_list = self.asin_entry.get()
        # if day not sat, it automatically set on 1
        day = self.last_day_entry.get()
        if day == '':
            day = '1'

        # if month not set, it automatically set on 1
        month = self.last_mounth_entry.get()
        if month == '':
            month = '1'
        month = calendar.month_name[int(month)]
        year = self.last_year_entry.get()
        end_date = day + " " + month + " " + year

        # creating part of filename
        filename = self.save_entry.get() + '/' + self.cat_entry.get()

        if os.path.isfile(asin_list):
            if os.path.splitext(asin_list)[1] == '.csv':
                asin_frame = pd.read_csv(asin_list, delimiter=';')
            elif os.path.splitext(asin_list)[1] == '.xlsx':
                asin_frame = pd.read_excel(asin_list)
            asin_list = list(asin_frame['Asin'])
        else:
            asin_list = [asin_list]

        # creating base class for reviews parsing
        if self.az_wb_var.get() == 'az':
            parser = parser_amazon
        elif self.az_wb_var.get() == 'wb':
            parser = patser_wb
        parser.scrap_feedbaks(sku_list=asin_list, end_date=end_date, filename=filename)

    def load_sales(self):
        """Get sales info for asins in list (only for AZ)"""
        asin_list = self.asin_entry.get()
        if os.path.isfile(asin_list):
            if os.path.splitext(asin_list)[1] == '.csv':
                asin_frame = pd.read_csv(asin_list, delimiter=';')
            elif os.path.splitext(asin_list)[1] == '.xlsx':
                asin_frame = pd.read_excel(asin_list)
            asin_list = list(asin_frame['Asin'])
        else:
            asin_list = [asin_list]
        h10.load_sales(asin_list=asin_list)

    def load_searches(self):
        """Get searches info for asins in list (only for AZ)"""
        key_list = self.asin_entry.get()
        if os.path.isfile(key_list):
            if os.path.splitext(key_list)[1] == '.csv':
                key_frame = pd.read_csv(key_list, delimiter=';')
            elif os.path.splitext(key_list)[1] == '.xlsx':
                key_frame = pd.read_excel(key_list)
            key_list = list(key_frame['Key'])
        else:
            key_list = [key_list]
        h10.load_searches(key_list=key_list, save_directory=self.save_entry.get())

    def load_trends(self):
        """Get selected info about keys"""
        region = self.region_entry.get()
        # if region is empty, set default region to
        if region == '':
            # region = 'US'
            region = ''
        by_region = self.get_region_var.get()
        by_global = self.get_global_var.get()
        by_country = self.get_by_country_var.get()
        related_topics = self.related_topics_var.get()
        related_searches = self.related_searches_var.get()
        suggested_topics = self.suggested_topics_var.get()
        savedir = self.save_entry.get()
        key_list = self.asin_entry.get()
        if os.path.isfile(key_list):
            if os.path.splitext(key_list)[1] == '.csv':
                key_frame = pd.read_csv(key_list, delimiter=';')
            elif os.path.splitext(key_list)[1] == '.xlsx':
                key_frame = pd.read_excel(key_list)
            key_list = list(key_frame['Key'])
        else:
            key_list = [key_list]
        if by_global:
            ct = Common_trends(kw_list=key_list, region=region, savedir=savedir)
            ct.get_global()

        if by_region:
            ct = Common_trends(kw_list=key_list, region=region, savedir=savedir)
            ct.get_region()

        if by_country:
            ct = Common_trends(kw_list=key_list, region=region, savedir=savedir)
            ct.get_by_country()

        if related_topics:
            ct = Common_trends(kw_list=key_list, region=region, savedir=savedir)
            ct.related_topics()

        if related_searches:
            ct = Common_trends(kw_list=key_list, region=region, savedir=savedir)
            ct.related_searches()

        if suggested_topics:
            ct = Common_trends(kw_list=key_list, region=region, savedir=savedir)
            ct.suggested_topics()


    def human_ready(self):
        """React on human interaction"""
        h10.human_inter = False


root = tk.Tk()
root.title("Parser App")
root.geometry("500x200")
root.resizable(False, False)
root.columnconfigure(3, minsize=50, weight=1)
root.columnconfigure(1, minsize=50, weight=1)

app = App(master=root)
app.load_sales_button.config(command=app.load_sales_thread)
app.load_search_button.config(command=app.load_searches_thread)
app.mainloop()
