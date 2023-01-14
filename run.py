from multiprocessing import Process
import JARVIS
from database import *
import datetime


if __name__ == "__main__":
    p1 = Process
    
db = Database()
day = datetime.datetime.timestamp(datetime.datetime(2023, 1, 18, 18, 0))
# print(db.execute(f"insert into Kalender (date, plan) values ({day}, 'Bowling with David');"))
print(db.execute(f"select * from kalender;"))