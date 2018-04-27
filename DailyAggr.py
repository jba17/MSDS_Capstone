# Purpose of program is to compress multiple raw data csv files into a single csv
# file for that day.  Raw files were generated through automatic queries using 
# tweepy and named under a standard naming convention (currency_YYYYMMDD-HHMMSS)
# Files are taken and saved in a predetermined folder structure as mapped out in
# www.github.com/JackNelson/Capstone
import os
import re

class DailyAggr:
    
    def __init__(self, folder_source, folder_dest):
        self.folder_source = folder_source
        self.folder_dest = folder_dest
    
    # Internal function extracting list of csv files in folder
    def _getFiles(self):
        path = str(os.getcwd()) + "/" + self.folder_source
        files = []
        # regex to get 8 digit day code in filename timestamp
        reg = re.compile("\d{8}")
        for csv_path in os.listdir(path):
            if reg.search(csv_path):
                files.append(csv_path)
        return files
    
    # Internal function creating list of unique day timestamps
    # _getDays(files = list of strings)
    def _getDays(self, files):
        days = []
        for csv_path in files:
            # regex to get 8 digit day code in filename timestamp
            day = re.search("\d{8}",csv_path).group(0)
            if day not in days:
                days.append(day)
        return days
    
    # Internal function appending csv files to single day csv
    # _aggrDays(files = list of strings, days = list of strings)
    def _aggrDays(self, files, days):
        for day in days:
            day_path = self.folder_dest + "/" + day + ".csv"
            day_file = open(day_path, "a")
            header = False
            
            for csv_path in files:
                if day in csv_path:
                    skip = 1
                    csv_file = open(self.folder_source + "/" + csv_path)
                    
                    if (header == False):
                        for line in csv_file:
                            day_file.write(line)
                            header = True
                            
                    else:
                        for line in csv_file:
                            if (skip == 0):
                                day_file.write(line)
                            else:
                                skip = 0
                    csv_file.close()
            day_file.close()

# External function to execute DailyAggr class functions for a list of crypyocurrencies           
def AggrDays(cryptos):
    
    for currency in cryptos:
        folder_source = "data/csv_dumps/"+currency
        folder_dest = "data/csv_daily/"+currency
        obj = DailyAggr(folder_source, folder_dest)
        files = obj._getFiles()
        days = obj._getDays(files)
        obj._aggrDays(files, days)
            
cryptos = ['Bitcoin', 'ETH', 'Ripple']
AggrDays(cryptos)