from flask import Flask, render_template, request, redirect
import sqlite3
import requests
import csv
import io

app = Flask(__name__)

DB = "aslm_live.db"

SHEET_ID = "1F98VyDkkxujPQH1E86osKDgkzwqH_gupwpejHDkFPG8"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Compositions"
)

EQUIPES = [
    "U13",
    "U15 A",
    "U15 B",
    "U18",
    "Senior A",
    "Senior B",
    "Vétéran"
]


def db():
    return sqlite3.connect(DB)


def init_db():

    c = db()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS matchs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipe TEXT,
        adversaire TEXT,
        domicile TEXT,
        stade TEXT,
        date_match TEXT,
        heure_match TEXT,
        score_aslm INTEGER DEFAULT 0,
        score_adv INTEGER DEFAULT 0,
        statut TEXT DEFAULT 'Avant match'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS buts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        minute TEXT,
        buteur TEXT
    )
    """)

    c.commit()
    c.close()


init_db()


def get_joueurs_match(equipe, date_match):

    try:

        csv_data = requests.get(
            CSV_URL,
            timeout=10
        ).text

        reader = csv.reader(
            io.StringIO(csv_data)
        )

        joueurs = []

        for row in reader:


            print("ROW =", row)

            if len(row) < 5:
                continue

            equipe_sheet = row[1].strip()
            date_sheet = row[2].strip()
            print(
                "FEUILLE :",
                equipe_sheet,
                "|",
                date_sheet
            )

            print(
                "MATCH :",
                equipe,
                "|",
                date_match
            )

            if date_sheet == date_match:   

                joueur = row[3].strip()

                if joueur:
                    joueurs.append(joueur)

        joueurs = list(dict.fromkeys(joueurs))

        return joueurs

    except Exception as e:

        print(
            "Erreur lecture Google Sheet :",
            e
        )

        return []


@app.route("/")
def index():

    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs ORDER BY id DESC"
    )

    matchs = cur.fetchall()

    c.close()

    return render_template(
        "index.html",
        matchs=matchs
    )


@app.route("/admin")
def admin():

    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs ORDER BY id DESC"
    )

    matchs = cur.fetchall()

    c.close()

    return render_template(
        "admin.html",
        matchs=matchs,
        equipes=EQUIPES
    )


@app.route("/create", methods=["POST"])
def create():

    c = db()
    cur = c.cursor()

    cur.execute("""
        INSERT INTO matchs(
            equipe,
            adversaire,
            domicile,
            stade,
            date_match,
            heure_match,
            statut
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        request.form["equipe"],
        request.form["adversaire"],
        request.form["domicile"],
        request.form["stade"],
        request.form["date_match"],
        request.form["heure_match"],
        "Avant match"
    ))

    c.commit()
    c.close()

    return redirect("/admin")


@app.route("/edit/<int:i>", methods=["GET", "POST"])
def edit(i):

    c = db()
    cur = c.cursor()

    if request.method == "POST":

        cur.execute("""
            UPDATE matchs
            SET equipe=?,
                adversaire=?,
                domicile=?,
                stade=?,
                date_match=?,
                heure_match=?
            WHERE id=?
        """,
        (
            request.form["equipe"],
            request.form["adversaire"],
            request.form["domicile"],
            request.form["stade"],
            request.form["date_match"],
            request.form["heure_match"],
            i
        ))

        c.commit()
        c.close()

        return redirect("/admin")

    cur.execute(
        "SELECT * FROM matchs WHERE id=?",
        (i,)
    )

    m = cur.fetchone()

    c.close()

    return render_template(
        "edit.html",
        m=m,
        equipes=EQUIPES
    )


@app.route("/delete/<int:i>")
def delete(i):

    c = db()
    cur = c.cursor()

    cur.execute(
        "DELETE FROM matchs WHERE id=?",
        (i,)
    )

    c.commit()
    c.close()

    return redirect("/admin")


@app.route("/match/<int:i>")
def match(i):

    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs WHERE id=?",
        (i,)
    )

    m = cur.fetchone()

    cur.execute(
        "SELECT minute,buteur FROM buts WHERE match_id=? ORDER BY id",
        (i,)
    )

    b = cur.fetchall()

    c.close()

    joueurs_compo = []

    try:

        equipe = m[1]
        date_match = m[5]

        joueurs_compo = get_joueurs_match(
            equipe,
            date_match
        )

        print("================================")
        print("Equipe :", equipe)
        print("Date :", date_match)
        print("JOUEURS TROUVES :", joueurs_compo)
        print("================================")

    except Exception as e:

        print("Erreur :", e)

    return render_template(
        "match.html",
        match=m,
        buts=b,
        joueurs_compo=joueurs_compo
    )


@app.route("/score/<int:i>/<t>")
def score(i, t):

    c = db()
    cur = c.cursor()

    actions = {
        "pa": "score_aslm = score_aslm + 1",
        "ma": """
            score_aslm =
            CASE
            WHEN score_aslm > 0
            THEN score_aslm - 1
            ELSE 0
            END
        """,
        "pv": "score_adv = score_adv + 1",
        "mv": """
            score_adv =
            CASE
            WHEN score_adv > 0
            THEN score_adv - 1
            ELSE 0
            END
        """
    }

    cur.execute(
        f"UPDATE matchs SET {actions[t]} WHERE id=?",
        (i,)
    )

    c.commit()
    c.close()

    return redirect(f"/match/{i}")


@app.route("/statut/<int:i>/<path:s>")
def statut(i, s):

    c = db()
    cur = c.cursor()

    cur.execute(
        "UPDATE matchs SET statut=? WHERE id=?",
        (s, i)
    )

    c.commit()
    c.close()

    return redirect(f"/match/{i}")


@app.route("/but/<int:i>", methods=["POST"])
def but(i):

    buteur = request.form["buteur"]

    if buteur == "AUTRE":
        buteur = request.form["autre_joueur"]

    c = db()
    cur = c.cursor()

    cur.execute(
        """
        INSERT INTO buts(
            match_id,
            minute,
            buteur
        )
        VALUES (?, ?, ?)
        """,
        (
            i,
            request.form["minute"],
            buteur
        )
    )

    cur.execute(
        """
        UPDATE matchs
        SET score_aslm = score_aslm + 1
        WHERE id=?
        """,
        (i,)
    )

    c.commit()
    c.close()

    return redirect(f"/match/{i}")


@app.route("/buteurs")
def buteurs():

    c = db()
    cur = c.cursor()

    cur.execute("""
        SELECT
            buteur,
            COUNT(*) as nb
        FROM buts
        GROUP BY buteur
        ORDER BY nb DESC
    """)

    rows = cur.fetchall()

    c.close()

    return render_template(
        "buteurs.html",
        rows=rows
    )

print("APP CHARGEE")

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )