import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os.path
import time 

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(filetypes=[("Книга Excel (*.xlsx)", "*.xlsx")])

dfs = pd.read_excel(file_path, sheet_name=None)
df = dfs[list(dfs)[0]]

columns = list(df.columns)
db_title = str(columns[0])

print("Конвертируем базу \"%s\"..." % db_title)

columns = columns[1:]

df = df.drop(db_title, axis=1)

columns_human = list(df.iloc[0])
columns_units = list(df.iloc[1])
columns_types = [(str(v)[:-1], True) if str(v)[-1] == "~" else (str(v), False) for v in list(df.iloc[2])]

df = df.drop([0,1,2], axis=0)

#print(pd.isna(columns_units[0]))
conversions = {
    "str": lambda x: str(x),
    "int": lambda x: int(x),
    "float": lambda x: float(x),
}

db_file = "%sdb" % file_path[0:-4]
if os.path.isfile(db_file):
    print("ОШИБКА! Файл %s уже существует! Переместите его или удалите, чтобы конвертировать базу." % db_file)
    time.sleep(5)
    quit()

con = sqlite3.connect(db_file)

cur = con.cursor()

query = '''CREATE TABLE IF NOT EXISTS database_settings
                                        (title TEXT)'''

cur.execute(query)

query = "INSERT INTO database_settings(title) VALUES(?)"
cur.execute(query, [db_title])

sql_types = {
    "int": "INTEGER",
    "str": "TEXT",
    "float": "REAL"
}

sql_table_columns = []
sql_table_human = []
sql_table_units = []
for i in range(len(columns)):
    types = columns_types[i]
    if not types[1]:
        sql_table_columns.append("%s %s" % (columns[i], sql_types[types[0]]))
        sql_table_human.append(columns_human[i])
        sql_table_units.append(columns_units[i])
        continue

    sql_table_columns.append("%s_vmin %s, %s_vmax %s" % (columns[i], sql_types[types[0]], columns[i], sql_types[types[0]]))
    sql_table_human.append(columns_human[i])
    sql_table_units.append(columns_units[i])
    sql_table_human.append(columns_human[i])
    sql_table_units.append(columns_units[i])


query = '''CREATE TABLE IF NOT EXISTS database
                                (%s)''' % (", ".join(sql_table_columns), )

cur.execute(query)

con.commit()

query = "PRAGMA table_info(database)"
res = cur.execute(query)
sql_columns = [c[1] for c in res.fetchall()]

query = '''CREATE TABLE IF NOT EXISTS database_definitions
                                (%s TEXT)''' % (" TEXT, ".join(sql_columns), )

cur.execute(query)

query = "INSERT INTO database_definitions(%s) VALUES(?%s)" % (", ".join(sql_columns), ", ?" * (len(sql_columns) - 1))
cur.execute(query, sql_table_human)

query = "INSERT INTO database_definitions(%s) VALUES(?%s)" % (", ".join(sql_columns), ", ?" * (len(sql_columns) - 1))
cur.execute(query, sql_table_units)

con.commit()

i_len = len(df)
i_p = 0

for index, row in df.iterrows():
    i_p += 1
    val = []
    for i in range(len(columns)):
        if pd.isna(row[columns[i]]):
            val.append(None)
            continue
        
        if not columns_types[i][1]:
            val.append(conversions[columns_types[i][0]](row[columns[i]]))
        else:
            vals = row[columns[i]].split("_")
            for v in vals:
                val.append(conversions[columns_types[i][0]](v))
    
    query = "INSERT INTO database(%s) VALUES(?%s)" % (", ".join(sql_columns), ", ?" * (len(sql_columns) - 1))
    cur.execute(query, val)

    con.commit()
    
    percent = int((i_p/i_len)*100)
    print("[%s] %i%%" % (("=" * (percent//5)) + (" " * (20 - (percent//5))), percent))


con.close()
print("Готово!")
time.sleep(5)