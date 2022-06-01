import sqlite3
from traceback import print_tb
import pandas as pd
from requests import delete


class DatabaseModule:
    def __init__(self, database_name,recreate_table=False):
        self.database_name = database_name
        if recreate_table:
            self.delete_table()
        self.create_table()
        

    def insert_data(self,dict):
        db = sqlite3.connect(self.database_name)
        db.execute(f'''INSERT INTO SolarData 
                   (time,solar_power, grid_power, house_power, twc_power, heater_power, heater_mode) 
                   VALUES ("{dict['time']}",{dict['solar_power']}, {dict['grid_power']}, {dict['house_power']}, {dict['twc_power']}, {dict['heater_power']}, "{dict['heater_mode']}")'''
                   )
        db.commit()
        db.close()
        
    def select_data_day(self,date):
        db = sqlite3.connect(self.database_name)
        df = pd.read_sql(f'''SELECT * FROM SolarData WHERE DATE(time)='{date}' ''', db)
        db.close()
        return df
    
    def create_table(self):
        db = sqlite3.connect(self.database_name)
        db.execute('''CREATE TABLE IF NOT EXISTS SolarData (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time DATETIME NOT NULL,
                solar_power INTERGER,
                grid_power INTERGER,
                house_power INTERGER,
                twc_power INTERGER,
                heater_power INTERGER,
                heater_mode TEXT
                )'''
            )
        db.close()
    
    def delete_table(self):
        db = sqlite3.connect(self.database_name)
        db.execute('''DROP TABLE IF EXISTS SolarData''')
        db.close()