from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from tinydb import TinyDB, Query
import os

app = Flask(__name__)
app.secret_key = "preprost-kljuc"

db = TinyDB("baza.json")
uporabniki_tabela = db.table("uporabniki")
mize_tabela = db.table("mize")

if not mize_tabela.all():
    for i in range(1,31):
        mize_tabela.insert({"stevilka_mize":i, "zasedana": False})

if not uporabniki_tabela.all():
    uporabniki_tabela.insert({"uporabnisko_ime" : "natakar1", "geslo":"natakar123", "vloga":"natakar"})
    uporabniki_tabela.insert({"uporabnisko_ime" : "kuhar1", "geslo":"kuhar123", "vloga":"kuhar"})

@app.route("/")
def start():
    return render_template("start.html")

@app.route("/izberi_vlogo", methods = ["POST"])
def izberi_vlogo():
    vloga = request.form.get('vloga')
    if vloga == 'stranka':
        return redirect(url_for('stranka_miza'))
    elif vloga in ['natakar', 'kuhar']:
        return redirect(url_for('prijava', vloga=vloga))
    else:
        flash('Izberi veljavno vlogo.')
        return redirect(url_for('start'))
    
@app.route("/stranka_miza", methods = ["GET", "POST"])
def stranka_miza():
    if request.method == 'POST':
        stevilka_mize = request.form.get('stevilka_mize')
        if stevilka_mize and stevilka_mize.isdigit() and 1 <= int(stevilka_mize) <= 30:
            stevilka_mize = int(stevilka_mize)
            Miza = Query()
            miza = mize_tabela.search(Miza.stevilka_mize == stevilka_mize)
            if miza and 'zasedana' in miza[0] and not miza[0]['zasedana']:
                mize_tabela.update({'zasedena': True}, Miza.stevilka_mize == stevilka_mize)
                app.config['stevilka_mize'] = stevilka_mize
                return redirect(url_for('stranka_stran'))
            else:
                flash('Miza je že zasedena ali ne obstaja.')
                return redirect(url_for('stranka_miza'))
        else:
            flash('Vnesi veljavno število mize (1–30).')
            return redirect(url_for('stranka_miza'))
    return render_template('stranka_miza.html')

@app.route('/stranka_stran')
def stranka_stran():
    stevilka_mize = app.config.get('stevilka_mize', 'Neznano')
    return render_template('stranka_stran.html', stevilka_mize=stevilka_mize)

@app.route('/prijava/<vloga>', methods=['GET', 'POST'])
def prijava(vloga):
    if request.method == 'POST':
        uporabnisko_ime = request.form.get('uporabnisko_ime')
        geslo = request.form.get('geslo')
        Uporabnik = Query()
        uporabnik = uporabniki_tabela.search(Uporabnik.uporabnisko_ime == uporabnisko_ime)
        if uporabnik and uporabnik[0]['geslo'] == geslo and uporabnik[0]['vloga'] == vloga:
            app.config['prijavljeni_uporabnik'] = uporabnisko_ime
            app.config['vloga_uporabnika'] = vloga
            return redirect(url_for(f'{vloga}_stran'))
        else:
            flash('Napačno uporabniško ime, geslo ali vloga.')
            return redirect(url_for('prijava', vloga=vloga))
    return render_template('prijava.html', vloga=vloga)

@app.route('/natakar_stran')
def natakar_stran():
    if app.config.get('vloga_uporabnika') != 'natakar':
        flash('Prijavi se kot Natakar.')
        return redirect(url_for('prijava', vloga='natakar'))
    return render_template('natakar_stran.html')

@app.route('/kuhar_stran')
def kuhar_stran():
    if app.config.get('vloga_uporabnika') != 'kuhar':
        flash('Prijavi se kot Kuhar.')
        return redirect(url_for('prijava', vloga='kuhar'))
    return render_template('kuhar_stran.html')

@app.route('/odjava')
def odjava():
    app.config.pop('prijavljeni_uporabnik', None)
    app.config.pop('vloga_uporabnika', None)
    app.config.pop('stevilka_mize', None)
    flash('Uspešno si se odjavil.')
    return redirect(url_for('start'))

@app.route('/stranka_odhod')
def stranka_odhod():
    stevilka_mize = app.config.get('stevilka_mize')
    if stevilka_mize and isinstance(stevilka_mize, int):
        Miza = Query()
        mize_tabela.update({'zasedena': False}, Miza.stevilka_mize == stevilka_mize)
    app.config.pop('stevilka_mize', None)
    flash('Miza je sproščena. Hvala za obisk!')
    return redirect(url_for('start'))

@app.route("/pobrisi_mize", methods = ["POST"])
def pobrisi_mize():
    if app.config.get("vloga_uporabnika") != "natakar":
        flash("samo natakar lahko pobriše zasedanost miz")
        return redirect(url_for("prijava",vloga="natakar"))
    mize_tabela.update({"zasedana" : False})
    flash("vse mize so proste")
    return redirect(url_for("natakar_stran"))

@app.route('/api/mize', methods=['GET'])
def api_mize():
    mize = [{'stevilka_mize': m['stevilka_mize'], 'zasedena': m['zasedena']} for m in mize_tabela.all()]
    return jsonify(mize)

app.run(debug=True)