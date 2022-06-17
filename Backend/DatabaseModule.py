import sqlite3
import pandas as pd
from datetime import date


class DatabaseModule:
    def __init__(self, database_name,recreate_table=False):
        self.database_name = database_name
        if recreate_table:
            self.delete_table()
        self.create_table()
        
    def insert_power_data(self,data):
        db = sqlite3.connect(self.database_name)
        db.execute(f'''REPLACE INTO HistoricPower 
                   (time,solar_power, grid_power, house_power, twc_power, heater_power, heater_mode) 
                   VALUES ("{data['time']}",{data['solar_power']}, {data['grid_power']}, {data['house_power']}, {data['twc_power']}, {data['heater_power']}, "{data['heater_mode']}")'''
                   )
        db.commit()
        db.close()
        self.update_energy_day()
        
    def select_power_day(self,date_):
        db = sqlite3.connect(self.database_name)
        df = pd.read_sql(f'''SELECT * FROM HistoricPower WHERE DATE(time)='{date_}' ''', db)
        db.close()
        return df
    
    def insert_energy_day(self,data,date_=date.today()):
        db = sqlite3.connect(self.database_name)
        if 'solar_predicted' in data:
            db.execute(f'''REPLACE INTO DailyEnergy
                    (date,solar_energy,solar_predicted,grid_energy, twc_energy, twc_green_precentage, heater_energy, heater_green_precentage, house_energy,house_green_precentage)
                    VALUES ("{date_}",{data['solar_energy']},{data['solar_predicted']}, {data['grid_energy']},
                    {data['twc_energy']}, {data['twc_green_precentage']},
                    {data['heater_energy']}, {data['heater_green_precentage']},
                    {data['house_energy']}, {data['house_green_precentage']}
                    )'''
                    )
        else:
            db.execute(f'''REPLACE INTO DailyEnergy
                    (date,solar_energy,grid_energy, twc_energy, twc_green_precentage, heater_energy, heater_green_precentage, house_energy,house_green_precentage)
                    VALUES ("{date_}",{data['solar_energy']}, {data['grid_energy']},
                    {data['twc_energy']}, {data['twc_green_precentage']},
                    {data['heater_energy']}, {data['heater_green_precentage']},
                    {data['house_energy']}, {data['house_green_precentage']}
                    )'''
                    )
        db.commit()
        db.close()
    
    def update_energy_day(self,date_=date.today()):
        # TODO Sum * minute
        db = sqlite3.connect(self.database_name)
        db.execute(f'''REPLACE INTO DailyEnergy(date,solar_energy,solar_predicted,grid_energy,twc_energy,heater_energy,house_energy)
                   SELECT
                   DATE(time) AS date,
                   (SUM(solar_power) * 1/60) as solar_energy,
                   (SELECT solar_predicted FROM DailyEnergy WHERE date=DATE(time)) as solar_predicted,
                   (SUM(grid_power) * 1/60) as grid_energy,
                   (SUM(twc_power) * 1 /60) as twc_energy,
                   (SUM(heater_power) * 1/60) as heater_energy,
                   (SUM(house_power) * 1/60) as house_energy
                   FROM HistoricPower
                   WHERE DATE(time)='{date_}'
                   ''')
        db.commit()
        db.close()
    
    def select_energy_day(self,date_=date.today()):
        db = sqlite3.connect(self.database_name)
        df = pd.read_sql(f'''SELECT * FROM DailyEnergy WHERE date='{date_}' ''', db)#WHERE date='{date}'
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
                solar_predicted INTERGER,
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
        
        
if __name__ == '__main__':
    import requests
    from datetime import datetime
    db = DatabaseModule('data/SolarDatabase.db',False)
    
    df = db.select_power_day(date.today())
    print(date)
    print(df)

    