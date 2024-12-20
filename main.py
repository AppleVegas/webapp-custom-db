from flask import Flask, render_template, request
from database import DataBase



db = DataBase("databases\\db1.db")
app = Flask(__name__)

@app.route("/")
def table():
    title = db.get_db_title()
    columns = db.get_columns()
    human = db.get_human()
    human_columns = human[0]
    human_measures = human[1]
    return render_template('table.html', 
                            title=title, 
                            columns=columns, 
                            human_columns=human_columns, 
                            human_measures=human_measures)


@app.route('/api/data')
def data():
    elements = db.get_all()
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    lengthf = request.args.get('test', type=str)
    print(lengthf)
    return {'data': [dict(row) for row in elements]}
app.run(debug=True)