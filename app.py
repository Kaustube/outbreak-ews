"""Flask wrapper for Vercel deployment"""
from flask import Flask, render_template, jsonify
import json
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    with open('results/metrics.json', 'r') as f:
        metrics = json.load(f)
    return jsonify(metrics)

@app.route('/api/data')
def get_data():
    # Load predictions data (first 100 rows for demo)
    df = pd.read_csv('data/predictions.csv.gz', nrows=100)
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)
