import sqlite3
from traceback import print_tb
import pandas as pd
from requests import delete
from datetime import date


class DatabaseModule:
    def __init__(self, database_name,recreate_table=False):
        self.database_name = database_name
        if recreate_table:
            self.delete_table()
        self.create_table()
        
    def insert_data(self,data):
        db = sqlite3.connect(self.database_name)
        db.execute(f'''INSERT INTO HistoricPower 
                   (time,solar_power, grid_power, house_power, twc_power, heater_power, heater_mode) 
                   VALUES ("{data['time']}",{data['solar_power']}, {data['grid_power']}, {data['house_power']}, {data['twc_power']}, {data['heater_power']}, "{data['heater_mode']}")'''
                   )
        db.commit()
        db.close()
        
    def select_data_day(self,date):
        db = sqlite3.connect(self.database_name)
        df = pd.read_sql(f'''SELECT * FROM HistoricPower WHERE DATE(time)='{date}' ''', db)
        db.close()
        return df
    
    def create_table(self):
        db = sqlite3.connect(self.database_name)
        db.execute('''CREATE TABLE IF NOT EXISTS HistoricPower (
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
        db.execute('''CREATE TABLE IF NOT EXISTS DailyEnergy (
                date DATE PRIMARY KEY DEFAULT CURRENT_DATE,
                solar_energy INTERGER,
                grid_energy INTERGER,
                twc_energy INTERGER,
                twc_green_precentage FLOAT,
                heater_energy INTERGER,
                heater_green_precentage FLOAT,
                house_energy INTERGER,
                house_green_precentage FLOAT
                )'''
            )
        db.close()
    
    def delete_table(self):
        db = sqlite3.connect(self.database_name)
        db.execute('''DROP TABLE IF EXISTS HistoricPower''')
        db.execute('''DROP TABLE IF EXISTS DailyEnergy''')
        db.close()
        
    def insert_daily_energy(self,data,date=date.today()):
        db = sqlite3.connect(self.database_name)
        db.execute(f'''REPLACE INTO DailyEnergy
                   (date,solar_energy,grid_energy, twc_energy, twc_green_precentage, heater_energy, heater_green_precentage, house_energy,house_green_precentage)
                   VALUES ("{date}",{data['solar_energy']}, {data['grid_energy']},
                   {data['twc_energy']}, {data['twc_green_precentage']},
                   {data['heater_energy']}, {data['heater_green_precentage']},
                   {data['house_energy']}, {data['house_green_precentage']}
                   )'''
                )
        db.commit()
        db.close()
    
    def select_daily_energy(self,date=date.today()):
        db = sqlite3.connect(self.database_name)
        df = pd.read_sql(f'''SELECT * FROM DailyEnergy''', db)
        db.close()
        return df

if __name__ == '__main__':
    db = DatabaseModule('data/SolarDatabase.db',True)
    
    db.insert_daily_energy({'solar_energy':100,'grid_energy':200,'twc_energy':300,'twc_green_precentage':0.5,'heater_energy':400,'heater_green_precentage':0.6,'house_energy':500,'house_green_precentage':0.7})
    db.insert_daily_energy({'solar_energy':50,'grid_energy':200,'twc_energy':300,'twc_green_precentage':0.5,'heater_energy':400,'heater_green_precentage':0.6,'house_energy':500,'house_green_precentage':0.7})
    db.insert_daily_energy({'solar_energy':50,'grid_energy':33,'twc_energy':300,'twc_green_precentage':0.5,'heater_energy':400,'heater_green_precentage':0.6,'house_energy':500,'house_green_precentage':0.7})
    db.insert_daily_energy({'solar_energy':50,'grid_energy':200,'twc_energy':100,'twc_green_precentage':0.5,'heater_energy':400,'heater_green_precentage':0.6,'house_energy':500,'house_green_precentage':0.7})
    
    df = db.select_daily_energy()
    print(df)
    
    