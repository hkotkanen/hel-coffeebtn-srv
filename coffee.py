from flask import Flask, request, redirect, jsonify, g
import arrow

app = Flask(__name__)
db_file = 'data/coffees.db'

@app.route('/coffees', methods=['GET', 'POST'])
def coffees():
    ct = arrow.now('Europe/Helsinki')
    if request.method == 'GET':
        return jsonify({'latest': stamper.get_latest()})

    if request.method == 'POST':
        stamper.push_new_ts(ct.isoformat())
        return jsonify({'latest': stamper.get_latest()})


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
            except:
                print('exception in open text file, returning current time')
                self.latest_ts = arrow.now('Europe/Helsinki').isoformat()
        return self.latest_ts

    def push_new_ts(self, iso_ts):
        self.latest_ts = iso_ts
        with open(self.db_file, 'a') as db:
            db.write(iso_ts + '\n')

if __name__ == '__main__':
    stamper = TimeStamper(db_file)
    app.run(host='0.0.0.0', debug=True)
