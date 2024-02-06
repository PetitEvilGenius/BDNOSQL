from flask import Flask, render_template, request, redirect, url_for, make_response
from pymongo import MongoClient
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# Configurare MongoDB
client = MongoClient('localhost', 27017)
db = client['exemplu_db']
colectie = db['finante']


def generate_pdf(venituri, cheltuieli, interogare, pagina_curenta=""):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.drawString(72, 800, f"Raport Financiar - Pagina: {pagina_curenta}")

    # Ajustări pentru secțiunea Venituri
    pdf.drawString(72, 780, "Venituri:")
    line_height = 15
    max_lines_per_page = 40
    current_line = 1

    for venit in venituri:
        if current_line > max_lines_per_page:
            pdf.showPage()  # Treci la o nouă pagină
            current_line = 1
            pdf.drawString(72, 780, "Venituri:")

        vertical_position = 780 - current_line * line_height
        pdf.drawString(72, vertical_position,
                       f"{venit['suma']} {venit['moneda']}, {venit['sursa']}, {venit['data_ora']}")
        current_line += 1

    # Ajustări pentru secțiunea Cheltuieli
    pdf.drawString(72, 350, "Cheltuieli:")
    for cheltuiala in cheltuieli:
        if current_line > max_lines_per_page:
            pdf.showPage()  # Treci la o nouă pagină
            current_line = 1
            pdf.drawString(72, 350, "Cheltuieli:")

        vertical_position = 350 - current_line * line_height
        pdf.drawString(72, vertical_position,
                       f"{cheltuiala['suma']} {cheltuiala['moneda']}, {cheltuiala['categorie']}, {cheltuiala['data_ora']}")
        current_line += 1

    # Ajustări pentru secțiunea Rezultate interogare
    pdf.drawString(72, 120, "Rezultate interogare:")
    for rezultat in interogare:
        if current_line > max_lines_per_page:
            pdf.showPage()  # Treci la o nouă pagină
            current_line = 1
            pdf.drawString(72, 120, "Rezultate interogare:")

        vertical_position = 120 - current_line * line_height
        pdf.drawString(72, vertical_position,
                       f"{rezultat['tip']}, {rezultat['suma']} {rezultat['moneda']}, {rezultat.get('sursa', '') if rezultat['tip'] == 'venit' else rezultat.get('categorie', '')}, {rezultat['data_ora']}")
        current_line += 1

    pdf.save()

    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    venituri = colectie.find({'tip': 'venit'})
    cheltuieli = colectie.find({'tip': 'cheltuiala'})
    return render_template('index.html', venituri=venituri, cheltuieli=cheltuieli)

@app.route('/adauga_venit', methods=['GET', 'POST'])
def adauga_venit():
    if request.method == 'POST':
        suma = request.form['suma_venit']
        moneda = request.form['moneda_venit']
        sursa = request.form['sursa_venit']
        data_ora = datetime.now()

        colectie.insert_one({'tip': 'venit', 'suma': suma, 'moneda': moneda, 'sursa': sursa, 'data_ora': data_ora})

    venituri = colectie.find({'tip': 'venit'})
    cheltuieli = colectie.find({'tip': 'cheltuiala'})

    return render_template('adauga_venit.html', venituri=venituri, cheltuieli=cheltuieli)

@app.route('/adauga_cheltuiala', methods=['GET', 'POST'])
def adauga_cheltuiala():
    categorii_cheltuieli = ['Mancare', 'Intretinere', 'Curent', 'Gaze', 'Internet', 'Telefonie', 'Sanatate', 'Investitii', 'Calatorii', 'Iesiri_in_oras', 'Diverse', 'Cadouri']

    if request.method == 'POST':
        suma = request.form['suma_cheltuiala']
        moneda = request.form['moneda_cheltuiala']
        categorie = request.form['categorie_cheltuiala']
        data_ora = datetime.now()

        colectie.insert_one({'tip': 'cheltuiala', 'suma': suma, 'moneda': moneda, 'categorie': categorie, 'data_ora': data_ora})

    venituri = colectie.find({'tip': 'venit'})
    cheltuieli = colectie.find({'tip': 'cheltuiala'})

    return render_template('adauga_cheltuiala.html', venituri=venituri, cheltuieli=cheltuieli, categorii_cheltuieli=categorii_cheltuieli)

@app.route('/interogare', methods=['GET', 'POST'])
def interogare():
    categorii_cheltuieli = ['Mancare', 'Intretinere', 'Curent', 'Gaze', 'Internet', 'Telefonie', 'Sanatate', 'Investitii', 'Calatorii', 'Iesiri_in_oras', 'Diverse', 'Cadouri']

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
        return render_template('interogare.html', finante=finante, categorii_cheltuieli=categorii_cheltuieli)

    return render_template('interogare.html', mesaj_eroare=None, categorii_cheltuieli=categorii_cheltuieli)

@app.route('/raport_venituri')
def raport_venituri():
    venituri = colectie.find({'tip': 'venit'})
    cheltuieli = colectie.find({'tip': 'cheltuiala'})
    interogare = []  # Adăugați aici rezultatele interogării dacă este cazul

    pdf_buffer = generate_pdf(venituri, cheltuieli, interogare, "Venituri")

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=raport_venituri.pdf'

    return response

@app.route('/raport_cheltuieli')
def raport_cheltuieli():
    venituri = colectie.find({'tip': 'venit'})
    cheltuieli = colectie.find({'tip': 'cheltuiala'})
    interogare = []  # Adăugați aici rezultatele interogării dacă este cazul

    pdf_buffer = generate_pdf(venituri, cheltuieli, interogare, "Cheltuieli")

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=raport_cheltuieli.pdf'

    return response

@app.route('/raport_interogare')
def raport_interogare():
    tip = request.args.get('tip', '')
    suma = request.args.get('suma', '')
    moneda = request.args.get('moneda', '')
    sursa = request.args.get('sursa', '')
    categorie = request.args.get('categorie', '')
    data = request.args.get('data', '')

    criterii = {}

    if tip:
        criterii['tip'] = tip
    if suma:
        criterii['suma'] = suma
    if moneda:
        criterii['moneda'] = moneda
    if sursa and tip == 'venit':
        criterii['sursa'] = sursa
    if categorie and tip == 'cheltuiala':
        criterii['categorie'] = categorie
    if data:
        criterii['data_ora'] = {"$regex": f"^{data}"}

    if not criterii:
        venituri = colectie.find({'tip': 'venit'})
        cheltuieli = colectie.find({'tip': 'cheltuiala'})
        interogare = colectie.find({})
    else:
        venituri = colectie.find({'tip': 'venit', **criterii})
        cheltuieli = colectie.find({'tip': 'cheltuiala', **criterii})
        interogare = colectie.find(criterii)

    pdf_buffer = generate_pdf(venituri, cheltuieli, interogare, "Interogare")

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=raport_interogare.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)
