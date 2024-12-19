import sqlite3

class DataBase():
    def __init__(self, path):
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def close(self):
        self.con.close()

    def query(self, query):
        self.cur.execute(query)
        self.con.commit()

    def get_all(self):
        query = "SELECT * FROM database"
        res = self.cur.execute(query)
        self.con.commit()
        return res.fetchall()
    
    def get_db_title(self) -> str:
        query = "SELECT * FROM database_settings LIMIT 1"
        res = self.cur.execute(query)
        self.con.commit()
        return res.fetchone()["title"]
    
    def get_columns(self) -> list:
        query = "PRAGMA table_info(database)"
        res = self.cur.execute(query)
        sql_columns = [c[1] for c in res.fetchall()]
        return sql_columns

    def get_human(self):
        query = "SELECT * FROM database_definitions LIMIT 2"
        res = self.cur.execute(query)
        return res.fetchall()
