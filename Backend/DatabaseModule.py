import sqlite3
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
                   (SOLAR_POWER, GRID_POWER, HOUSE_POWER, TWC_POWER, HEAT_POWER, HEATER_MODE) 
                   VALUES ({dict['SOLAR_POWER']}, {dict['GRID_POWER']}, {dict['HOUSE_POWER']}, {dict['TWC_POWER']}, {dict['HEAT_POWER']}, "{dict['HEATER_MODE']}")'''
                   )
        db.commit()
        db.close()
        
    def select_data_day(self,date):
        db = sqlite3.connect(self.database_name)
        df = pd.read_sql(f'''SELECT * FROM SolarData WHERE DATE(DATETIME)='{date}' ''', db)
        db.close()
        return df
    
    def create_table(self):
        db = sqlite3.connect(self.database_name)
        db.execute('''CREATE TABLE IF NOT EXISTS SolarData (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                INSERTTIME DATETIME DEFAULT CURRENT_TIMESTAMP,
                SOLAR_POWER INTERGER,
                GRID_POWER INTERGER,
                HOUSE_POWER INTERGER,
                TWC_POWER INTERGER,
                HEAT_POWER INTERGER,
                HEATER_MODE TEXT
                )'''
            )
        db.close()
    
    def delete_table(self):
        db = sqlite3.connect(self.database_name)
        db.execute('''DROP TABLE IF EXISTS SolarData''')
        db.close()