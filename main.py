from flask import Flask, render_template
from database import DataBase



db = DataBase("databases\\db1.db")
app = Flask(__name__)

@app.route("/")
def hello_world():
    title = db.get_db_title()
    columns = db.get_columns()
    human = db.get_human()
    human_columns = human[0]
    human_measures = human[1]
    elements = db.get_all()
    return render_template('table.html', 
                            title=title, 
                            columns=columns, 
                            human_columns=human_columns, 
                            human_measures=human_measures,
                            elements=elements)


app.run(debug=True)