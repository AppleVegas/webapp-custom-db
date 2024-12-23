import sqlite3

def get_filter_query(filter):
    where = []
    for param in filter:

        if param["type"] == "TEXT":
            where.append(f"{param['name']} LIKE \"%{param['value']}%\"")
            continue
        
        vmin, vmax = param["value"].split("_")

        if param["ranged"]:
            if vmin:
                where.append(f"{param['name']}_vmin <= {vmin} AND {param['name']}_vmax >= {vmin}")
            if vmax:
                where.append(f"{param['name']}_vmax >= {vmax} AND {param['name']}_vmin <= {vmax}")
            continue
            
        if vmin:
            where.append(f"{param['name']} >= {vmin}")
        if vmax:
            where.append(f"{param['name']} <= {vmax}")

    return " AND ".join(where) if where else None

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
    
    def get_filtered(self, filter: list, start: int = 0, length: int = 10, order = "asc", ordercol = 0):
        
        where = get_filter_query(filter)


        if where:
            query = "SELECT * FROM database WHERE %s" % where
        else:
            query = "SELECT * FROM database"
        
        query += f" ORDER BY {ordercol} {order.upper()}"

        query += " LIMIT %i,%i" % (start, length)
        res = self.cur.execute(query)
        self.con.commit()
        return res.fetchall()
    
    def get_total_filtered(self, filter: list):
        
        where = get_filter_query(filter)

        if where:
            query = "SELECT COUNT(1) FROM database WHERE %s" % where
        else:
            query = "SELECT COUNT(1) FROM database"
        
        res = self.cur.execute(query)
        self.con.commit()
        return res.fetchone()[0]

    def get_db_title(self) -> str:
        query = "SELECT * FROM database_settings LIMIT 1"
        res = self.cur.execute(query)
        self.con.commit()
        return res.fetchone()["title"]
    
    def get_columns(self) -> list:
        query = "PRAGMA table_info(database)"
        res = self.cur.execute(query)
        sql_columns = [c["name"] for c in res.fetchall()]
        return sql_columns
    
    def get_total_rows(self) -> int:
        query = "SELECT COUNT(1) FROM database"
        res = self.cur.execute(query)
        self.con.commit()
        return res.fetchone()[0]
    
    def get_datatypes(self) -> dict:
        query = "PRAGMA table_info(database)"
        res = self.cur.execute(query)
        types = {c["name"]:c["type"] for c in res.fetchall()}
        return types

    def get_human(self):
        query = "SELECT * FROM database_definitions LIMIT 2"
        res = self.cur.execute(query)
        return res.fetchall()
