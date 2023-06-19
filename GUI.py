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
from datetime import datetime

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        """Main window with load from api and load from files blocks"""
        self.asin_label = tk.Label(self, text="ASIN:")
        self.asin_label.grid(row=0, column=0, sticky=tk.W)
        self.asin_entry = tk.Entry(self)
        self.asin_entry.grid(row=0, column=1)
        self.asin_button = tk.Button(self, text="Browse ASIN file...", command=self.browse_asin_file)
        self.asin_button.grid(row=0, column=2)

        self.az_wb_var = tk.StringVar()
        self.az_wb_var.set("az")
        self.rb01 = tk.Radiobutton(self, text="Wildberries", variable=self.az_wb_var, value="wb")
        self.rb02 = tk.Radiobutton(self, text="Amazon", variable=self.az_wb_var, value="az")

        self.rb01.grid(row=1, column=1, sticky=tk.N)
        self.rb02.grid(row=1, column=0, sticky=tk.N)

        self.date_label= tk.Label(self, text="Load up to:")
        self.date_label.grid(row=2, column=0,columnspan=3, sticky=tk.N)

        self.last_day = tk.Label(self, text="Day:")
        self.last_day.grid(row=4, column=0, sticky=tk.W)
        self.last_day_entry = tk.Entry(self)
        self.last_day_entry.grid(row=3, column=0)

        self.last_mounth = tk.Label(self, text="Mounth:")
        self.last_mounth.grid(row=4, column=1, sticky=tk.W)
        self.last_mounth_entry = tk.Entry(self)
        self.last_mounth_entry.grid(row=3, column=1)

        self.last_year = tk.Label(self, text="Year:")
        self.last_year.grid(row=4, column=2, sticky=tk.W)
        self.last_year_entry = tk.Entry(self)
        self.last_year_entry.grid(row=3, column=2)

        self.cat_label = tk.Label(self, text="Category name:")
        self.cat_label.grid(row=5, column=0, sticky=tk.W)
        self.cat_entry = tk.Entry(self)
        self.cat_entry.grid(row=5, column=1)

        self.save_label = tk.Label(self, text="Save directory:")
        self.save_label.grid(row=6, column=0, sticky=tk.W)
        self.save_entry = tk.Entry(self)
        self.save_entry.grid(row=6, column=1)
        self.save_button = tk.Button(self, text="Browse...", command=self.browse_save_directory)
        self.save_button.grid(row=6, column=2)

        self.load_button = tk.Button(self, text="Load feedbacks...", command=self.load_feedbacks)
        self.load_button.grid(row=7, column=0)

        self.load_sales_button = tk.Button(self, text="Load sales...", command=self.load_sales)
        self.load_sales_button.grid(row=7, column=1)

        self.human_interraction = tk.Button(self, text="Ready!", command=self.human_ready)
        self.human_interraction.grid(row=7, column=2)

    def update_human_button_state(self):
        if h10.human_inter:  # Условие для включения/выключения кнопки
            self.human_interraction.config(state=tk.NORMAL)  # Включить кнопку
        else:
            self.human_interraction.config(state=tk.DISABLED)  # Выключить кнопку

    def load_feedbacks_thread(self):
        threading.Thread(target=self.load_feedbacks).start()

    def load_sales_thread(self):
        threading.Thread(target=self.load_sales).start()

    def browse_save_directory(self):
        """Get dir to save loaded files"""
        save_directory = filedialog.askdirectory()
        self.save_entry.delete(0, tk.END)
        self.save_entry.insert(0, save_directory)

    def browse_asin_file(self):
        """Get asin from file"""
        filetypes = [("CSV files", "*.csv"), ("XLSX files", "*.xlsx")]
        directory = filedialog.askopenfilenames(initialdir=".", filetypes=filetypes)
        self.asin_entry.delete(0, tk.END)
        self.asin_entry.insert(0, directory)


    def load_feedbacks(self):
        asin_list=self.asin_entry.get()
        day=self.last_day_entry.get()
        if day == '':
            day='1'
        month=self.last_mounth_entry.get()
        if month == '':
            month='1'
        month = calendar.month_name[int(month)]
        year=self.last_year_entry.get()
        end_date=day + " " + month + " " + year
        filename=self.save_entry.get()+'/'+self.cat_entry.get()

        if os.path.isfile(asin_list):
            if os.path.splitext(asin_list)[1] == '.csv':
                asin_frame = pd.read_csv(asin_list, delimiter=';')
            elif os.path.splitext(asin_list)[1] == '.xlsx':
                asin_frame = pd.read_excel(asin_list)
            asin_list = list(asin_frame['Asin'])
        else:
            asin_list=[asin_list]

        if self.az_wb_var.get() == 'az':
            parser=parser_amazon
        elif self.az_wb_var.get() == 'wb':
            parser=patser_wb
        parser.scrap_feedbaks(sku_list=asin_list, end_date=end_date, filename=filename)

    def load_sales(self):
        asin_list = self.asin_entry.get()
        if os.path.isfile(asin_list):
            if os.path.splitext(asin_list)[1] == '.csv':
                asin_frame = pd.read_csv(asin_list, delimiter=';')
            elif os.path.splitext(asin_list)[1] == '.xlsx':
                asin_frame = pd.read_excel(asin_list)
            asin_list = list(asin_frame['Asin'])
        else:
            asin_list=[asin_list]
        h10.load_sales(asin_list=asin_list)

    def human_ready(self):
        h10.human_inter=False

root = tk.Tk()
root.title("Parser App")
root.geometry("450x200")
root.resizable(False, False)
root.columnconfigure(3, minsize=50, weight=1)
root.columnconfigure(1, minsize=50, weight=1)

app = App(master=root)
app.load_button.config(command=app.load_feedbacks_thread)  # Запуск load_feedbacks в отдельном потоке
app.load_sales_button.config(command=app.load_sales_thread)
app.mainloop()
