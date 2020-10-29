from flask import Flask, render_template, request
import mtginfo


app = Flask(__name__)
m = mtginfo.MtgDatabase()


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/results', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        deck = request.form['decklist']
        m.load_stats(deck)
        return m.print_stats_str()


app.run(port=5400, debug=True)
