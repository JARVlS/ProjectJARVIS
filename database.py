import sqlite3 as sql
from datetime import datetime


class Database:
    def __init__(self) -> None:
        self.con = sql.connect("jarvis_database.sqlite")

        self.cur = self.con.cursor()
        self.cur.execute(
            "create table if not exists kalender(id integer primary key, date timestamp not null,  plan varchar);"
        )
        self.con.commit()

        print("---CONNECTION TO DATABASE SUCCESSFULL---")

    def execute(self, sql_statement: str) -> dict:
        """Only accepts complete sql (sqlite3) statements and returns dict with {success: bool, data:dict, error}"""
        return_value = {
            "success": False,
            "data": {},
            "error": "Statement not valid"
        }
        if sql.complete_statement(sql_statement):
            sql_statement = sql_statement.strip()
            try: 
                self.cur.execute(sql_statement)
                return_value["success"] = True
                return_value["data"] = self.cur.fetchall()
                return_value["error"] = None
                self.con.commit()
            except sql.Error as e:
                return_value["success"] = False
                return_value["data"] = {}
                return_value["error"] = e.args[0]
                   
        return return_value
    
    def insert(self, date: datetime.timestamp, plan: str)->bool:
        try: 
            self.cur.execute("insert into kalender (date, plan) values (?, ?)", (date, plan))
            return {"success": True, "error": None}
        except sql.Error as e:
            return {"success": False, "error": e.args[0]}
        
    def delete(self, id: int):
        
        
    
if __name__ == "__main__":
    d = Database()