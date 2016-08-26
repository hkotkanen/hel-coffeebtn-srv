from flask import Flask, request, redirect, jsonify, g, render_template
import arrow

app = Flask(__name__)
db_file = 'coffees.db'

@app.route('/api/coffees', methods=['GET', 'POST'])
def coffees():
    ct = arrow.now('Europe/Helsinki')
    if request.method == 'GET':
        return jsonify({'latest': stamper.get_latest()})

    if request.method == 'POST':
        # save current time in db as the latest
        stamper.push_new_ts(ct.isoformat())
        # send message to slack?
        # send message to yammer?
        # maybe send message to all connected browser websockets?
        return jsonify({'latest': stamper.get_latest()})

@app.route('/coffee', methods=['GET'])
def render_coffees():
    return render_template('coffee.html', latest=stamper.get_latest())


class TimeStamper():
    def __init__(self, dbfile):
        print('initializing stamper')
        self.latest_ts = None
        self.db_file = dbfile

    def get_latest(self):
        if not self.latest_ts:
            try:
                with open(self.db_file, 'r') as db:
                    print('fetching latest from file')
                    self.latest_ts = db.readlines()[-1]
            except IOError:
                print('Couldn\'t open db file.')
                self.latest_ts = "2000-01-01"
        return self.latest_ts

    def push_new_ts(self, iso_ts):
        self.latest_ts = iso_ts
        with open(self.db_file, 'a') as db:
            db.write(iso_ts + '\n')

if __name__ == '__main__':
    stamper = TimeStamper(db_file)
    app.run(host='0.0.0.0', debug=True)
