from flask import Flask, render_template, request,  send_from_directory
from database import DataBase
import threading


DB_NAME = "db1"


lock = threading.Lock()

def form_freq(hz):
    if hz < 0:
        raise ValueError("Frequency value must be non-negative.")

    if hz < 1_000:
        return f"{hz} Hz"
    elif hz < 1_000_000:
        return f"{hz / 1_000:.2f} kHz"
    elif hz < 1_000_000_000:
        return f"{hz / 1_000_000:.2f} MHz"
    else:
        return f"{hz / 1_000_000_000:.2f} GHz"

db = DataBase(f"databases\\{DB_NAME}.db")
app = Flask(__name__)

title = db.get_db_title()
columns = db.get_columns()
column_types = db.get_datatypes()
human = db.get_human()
human_columns = human[0]
human_measures = human[1]
total_rows = db.get_total_rows()

table_columns = {}
for column in columns:
    id = column
    label = human_columns[column]
    is_ranged = False
    if len(column) > 5:
        if id[:-5] in table_columns.keys():
            continue
        if id[-5:] == "_vmin" or id[-5:] == "_vmax":
            id = id[:-5]
            is_ranged = True

    is_hz = False
    if human_measures[column]:
        label += ", " + human_measures[column]
        is_hz = human_measures[column] == "Hz"

    table_columns[id] = (label, column_types[column], is_hz, is_ranged)

@app.route("/")
def table():
    return render_template('table.html', 
                            title=title, 
                            table_columns=table_columns)

@app.route("/sheets/<path:path>")
def sheets(path):
    return send_from_directory(f'databases/{DB_NAME}', path + ".pdf")

@app.route('/api/data')
def data():
    searchparams = []
    i = 0
    for k, v in table_columns.items():
        val = request.args.get(f'columns[{i}][search][value]')
        if val:
            searchparams.append({
                "name": k,
                "value": val,
                "type": v[1],
                "ranged": v[3]
                })
        i += 1
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)

    try:
        lock.acquire(True)
        elements = db.get_filtered(searchparams, start, length)
        total_filtered = db.get_total_filtered(searchparams)
    finally:
        lock.release()

    column_data = []
    for element in elements:
        row_data = {}
        for column in table_columns.keys():
            if (column + "_vmin") in element.keys() and (column + "_vmax") in element.keys():
                vmin = element[column + "_vmin"]
                vmax = element[column + "_vmax"]
                is_hz = table_columns[column][2]
                row_data[column] = (form_freq(vmin) if is_hz else str(vmin)) + " - " + (form_freq(vmax) if is_hz else str(vmax))
                continue

            if not element[column]:
                row_data[column] = "Не указано"
            else:
                is_hz = table_columns[column][2]
                row_data[column] = (form_freq(vmin) if is_hz else element[column])

        column_data.append(row_data)
                

    return {
        'data': column_data,
        'recordsFiltered': total_filtered,
        'recordsTotal': total_rows,
        'draw': request.args.get('draw', type=int),
        }
app.run(debug=True)