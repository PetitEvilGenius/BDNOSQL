from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Configurare MongoDB
client = MongoClient('localhost', 27017)
db = client['exemplu_db']
colectie = db['finante']

@app.route('/')
def index():
    return render_template('index.html')

# ...

@app.route('/interogare', methods=['GET', 'POST'])
def interogare():
    if request.method == 'POST':
        tip = request.form.get('tip')
        suma = request.form.get('suma')
        moneda = request.form.get('moneda')
        sursa = request.form.get('sursa')
        categorie = request.form.get('categorie')
        data = request.form.get('data')

        criterii = {}

        if tip:
            criterii['tip'] = tip
        if suma:
            criterii['suma'] = suma
        if moneda:
            criterii['moneda'] = moneda
        if sursa:
            criterii['sursa'] = sursa
        if categorie:
            criterii['categorie'] = categorie
        if data:
            criterii['data_ora'] = {'$regex': data}

        if not criterii:
            return render_template('interogare.html', mesaj_eroare='Completați cel puțin un câmp pentru a efectua interogarea.')

        finante = colectie.find(criterii)
        return render_template('interogare.html', finante=finante)

    return render_template('interogare.html', mesaj_eroare=None)

# ...

@app.route('/adauga_venit', methods=['GET', 'POST'])
def adauga_venit():
    if request.method == 'POST':
        suma = request.form['suma_venit']
        moneda = request.form['moneda_venit']
        sursa = request.form['sursa_venit']
        data_ora = datetime.now()

        colectie.insert_one({'tip': 'venit', 'suma': suma, 'moneda': moneda, 'sursa': sursa, 'data_ora': data_ora})

        return redirect(url_for('index'))

    return render_template('adauga_venit.html')

@app.route('/adauga_cheltuiala', methods=['GET', 'POST'])
def adauga_cheltuiala():
    if request.method == 'POST':
        suma = request.form['suma_cheltuiala']
        moneda = request.form['moneda_cheltuiala']
        categorie = request.form['categorie_cheltuiala']
        data_ora = datetime.now()

        colectie.insert_one({'tip': 'cheltuiala', 'suma': suma, 'moneda': moneda, 'categorie': categorie, 'data_ora': data_ora})

        return redirect(url_for('index'))

    return render_template('adauga_cheltuiala.html')

if __name__ == '__main__':
    app.run(debug=True)
