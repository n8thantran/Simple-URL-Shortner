import json
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "lmao this is a secret key"
hashids = Hashids(min_length=10, salt=app.config['SECRET_KEY'])

def load_data():
    with open('data.json', 'r') as file:
        return json.load(file)

def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('You need to put a url dingus')
            return redirect(url_for('index'))
        
        data = load_data()
        new_id = str(len(data) + 1)
        
        url_data = {
            new_id: {
                "timeStamp": datetime.now().isoformat(),
                "originalUrl": url,
                "clicksAmount": 0
            }
        }

        data.update(url_data)
        save_data(data)

        hashid = hashids.encode(int(new_id))
        short_url = f"{request.host_url}{hashid}"

        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

@app.route('/<id>')
def url_redirect(id):
    data = load_data()

    original_id = hashids.decode(id)
    if original_id:
        original_id = str(original_id[0])
        originalUrl = data[original_id]['originalUrl']
        data[original_id]['clicksAmount'] += 1
        save_data(data)
        return redirect(originalUrl)
    else:
        flash('this url dont work bud')
        return redirect(url_for('index'))
    
@app.route('/stats')
def stats():
    data = load_data()
    urls_data = {}
    for key, value in data.items():
        urls_data[key] = {
            "timeStamp": value["timeStamp"],
            "originalUrl": value["originalUrl"],
            "clicksAmount": value["clicksAmount"]
        }

    formatted_urls = []
    for key, value in urls_data.items():
        url_entry = value.copy()
        url_entry['short_url'] = request.host_url + hashids.encode(int(key))
        formatted_urls.append(url_entry)

    return render_template('stats.html', urls=formatted_urls)