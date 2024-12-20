from flask import Flask, render_template, request
from database import DataBase



db = DataBase("databases\\db1.db")
app = Flask(__name__)

title = db.get_db_title()
columns = db.get_columns()
column_types = db.get_datatypes()
human = db.get_human()
human_columns = human[0]
human_measures = human[1]
total_rows = db.get_total_rows()

human_labels = []

for column in columns:
    label = human_columns[column]
    if len(column) > 5:
        if column[-5:] == "_vmin":
            label += " (мин.)" 
        elif column[-5:] == "_vmax":
            label += " (макс.)" 
    if human_measures[column]:
        label += ", " + human_measures[column]

    human_labels.append(label)

@app.route("/")
def table():
    return render_template('table.html', 
                            title=title, 
                            columns=columns, 
                            labels=human_labels)


@app.route('/api/data')
def data():
    searchparams = []
    for i in range(len(columns)):
        val = request.args.get(f'columns[{i}][search][value]')
        if val:
            searchparams.append([columns[i], val, column_types[i]])
    
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    elements = db.get_filtered(searchparams, start, length)
    total_filtered = db.get_total_filtered(searchparams)
    print(searchparams)
    return {
        'data': [dict(row) for row in elements],
        'recordsFiltered': total_filtered,
        'recordsTotal': total_rows,
        'draw': request.args.get('draw', type=int),
        }
app.run(debug=True)