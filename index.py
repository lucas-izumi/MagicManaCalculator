from flask import Flask, render_template, request
import mtginfo
# from gevent.pywsgi import WSGIServer


app = Flask(__name__)
m = mtginfo.MtgDatabase()


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/results', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        deck = request.form['decklist']
        response = m.load_stats(deck)
        if response != mtginfo.ERR_NO_ERROR:
            return response
        else:
            return render_template("results.html",
                                   total_cmc=int(m.total_cmc),
                                   total_color_mana_cost=m.total_coloured_mana_cost,
                                   total_cards=m.total_cards,
                                   average_mana=m.average_mana_per_card,
                                   suggested_mana=m.suggested_total_mana,
                                   white_mana=m.suggested_mana_colors['W'],
                                   blue_mana=m.suggested_mana_colors['U'],
                                   black_mana=m.suggested_mana_colors['B'],
                                   red_mana=m.suggested_mana_colors['R'],
                                   green_mana=m.suggested_mana_colors['G'],
                                   )


# app.run(port=5400, debug=True)
# app.run(host='0.0.0.0', port=5000)
# http_server = WSGIServer(('', 5000), app)
# http_server.serve_forever()
app.run()
