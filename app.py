from flask import Flask, render_template, request, redirect, session
<<<<<<< HEAD
from datetime import datetime
=======
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

import sqlite3
import requests
import csv
import io
import os

<<<<<<< HEAD
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

gc = gspread.authorize(credentials)

classeur = gc.open_by_key(
    "1F98VyDkkxujPQH1E86osKDgkzwqH_gupwpejHDkFPG8"
)

sheet_matchs = classeur.worksheet("matchs")
sheet_buts = classeur.worksheet("buts")

def creer_match_google():

    lignes = sheet_matchs.get_all_values()

    return len(lignes)

=======
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
app = Flask(__name__)

app.secret_key = "ASLM_SECRET_2026"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB = os.path.join(
    BASE_DIR,
    "aslm_live.db"
)

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

<<<<<<< HEAD
=======
    print("BASE SQLITE :", DB)

>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
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

<<<<<<< HEAD
=======

            print("ROW =", row)

>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
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
<<<<<<< HEAD
        
def get_matchs_google():

    lignes = sheet_matchs.get_all_values()

    matchs = []

    # Ignore la ligne d'entête
    for row in lignes[1:]:

        if len(row) < 12:
            continue

        # colonne actif
        if row[11].strip().upper() != "OUI":
            continue

        matchs.append(row)

    return matchs
    
def get_buts_google(match_id):

    lignes = sheet_buts.get_all_values()

    buts = []

    for row in lignes[1:]:

        if len(row) < 3:
            continue

        if str(row[0]) == str(match_id):

            buts.append([
                row[1],  # minute
                row[2]   # buteur
            ])

    return buts
    
def ajouter_but_google(match_id, minute, buteur):

    sheet_buts.append_row([
        match_id,
        minute,
        buteur
    ])    

def get_match_google(match_id):

    lignes = sheet_matchs.get_all_values()

    for row in lignes[1:]:

        if len(row) < 12:
            continue

        if row[0] == str(match_id):

            return row

    return None 

from datetime import datetime

def calcul_minute_match(match):

    try:

        statut = match[8]

        if statut == "Terminé":
            return match[13]

        if statut == "Mi-temps":
            return 45

        heure_debut = match[12]

        if not heure_debut:
            return 0

        debut = datetime.strptime(
            heure_debut,
            "%Y-%m-%d %H:%M:%S"
        )

        maintenant = datetime.now()

        minutes = int(
            (maintenant - debut).total_seconds() / 60
        )

        base = int(match[13])

        return base + minutes

    except Exception as e:

        print("Erreur chrono :", e)

        return 0
    
def update_score_google(match_id, colonne, valeur):

    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(lignes[1:], start=2):

        if row[0] == str(match_id):

            sheet_matchs.update_cell(
                index,
                colonne,
                valeur
            )

            break

def get_matchs_public():

    lignes = sheet_matchs.get_all_values()

    matchs = []

    for row in lignes[1:]:

        if len(row) < 12:
            continue

        if row[11].strip().upper() != "OUI":
            continue

        matchs.append(row)

    return matchs
    
@app.route("/demarrer_match/<int:i>")
def demarrer_match(i):

    if not session.get("admin"):
        return redirect("/login")

    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(lignes[1:], start=2):

        if row[0] == str(i):

            # Reprise après mi-temps
            if str(row[14]) == "2":

                maintenant = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # nouvelle heure de départ
                sheet_matchs.update_cell(
                    index,
                    13,
                    maintenant
                )

                # statut
                sheet_matchs.update_cell(
                    index,
                    9,
                    "En cours"
                )

                # minute repart à 45
                sheet_matchs.update_cell(
                    index,
                    14,
                    45
                )


            else:

                # Premier démarrage
                maintenant = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                sheet_matchs.update_cell(
                    index,
                    13,
                    maintenant
                )

                sheet_matchs.update_cell(
                    index,
                    14,
                    0
                )

                sheet_matchs.update_cell(
                    index,
                    15,
                    1
                )

                sheet_matchs.update_cell(
                    index,
                    9,
                    "En cours"
                )

            break

    return redirect(f"/match/{i}")
@app.route("/test_matchs_google")
def test_matchs_google():

    matchs = get_matchs_google()

    return str(matchs)    
=======
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login = request.form["login"]
        password = request.form["password"]

        if (
            login == "admin"
            and
            password == "ASLM2026"
        ):

            session["admin"] = True

            return redirect("/admin")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/")
def index():

<<<<<<< HEAD
    matchs = get_matchs_public()

    matchs_affichage = []

    for m in matchs:

        try:
            minute_match = calcul_minute_match(m)
        except:
            minute_match = 0

        buts = get_buts_google(m[0])

        matchs_affichage.append(
            {
                "match": m,
                "minute_match": minute_match,
=======
    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs ORDER BY id DESC"
    )

    matchs = cur.fetchall()

    matchs_avec_buts = []

    for m in matchs:

        cur.execute(
            """
            SELECT minute,buteur
            FROM buts
            WHERE match_id=?
            ORDER BY id
            """,
            (m[0],)
        )

        buts = cur.fetchall()

        matchs_avec_buts.append(
            {
                "match": m,
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
                "buts": buts
            }
        )

<<<<<<< HEAD
    return render_template(
        "index.html",
        matchs_affichage=matchs_affichage
    )

=======
    c.close()

    return render_template(
        "index.html",
        matchs_avec_buts=matchs_avec_buts
    )


>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

<<<<<<< HEAD
    matchs = get_matchs_google()
=======
    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs ORDER BY id DESC"
    )

    matchs = cur.fetchall()

    c.close()
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return render_template(
        "admin.html",
        matchs=matchs,
        equipes=EQUIPES
    )


@app.route("/create", methods=["POST"])
def create():

<<<<<<< HEAD
    print("CREATE APPELE")

    new_id = creer_match_google()

    print("Avant append_row")

    sheet_matchs.append_row([
        new_id,
        request.form["equipe"],
        request.form["adversaire"],
        request.form["date_match"],
        request.form["stade"],
        request.form["heure_match"],
        request.form["domicile"],
        request.form["domicile"],
        "Avant match",
        0,
        0,
        "OUI"
    ])

    print("Après append_row")
=======
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
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return redirect("/admin")


@app.route("/edit/<int:i>", methods=["GET", "POST"])
def edit(i):

<<<<<<< HEAD
    if not session.get("admin"):
        return redirect("/login")

    # Enregistrement
    if request.method == "POST":

        lignes = sheet_matchs.get_all_values()

        for index, row in enumerate(
            lignes[1:],
            start=2
        ):

            if row[0] == str(i):

                sheet_matchs.update_cell(index, 2, request.form["equipe"])
                sheet_matchs.update_cell(index, 3, request.form["adversaire"])
                sheet_matchs.update_cell(index, 4, request.form["date_match"])
                sheet_matchs.update_cell(index, 5, request.form["stade"])
                sheet_matchs.update_cell(index, 6, request.form["heure_match"])
                sheet_matchs.update_cell(index, 7, request.form["domicile"])
                sheet_matchs.update_cell(index, 8, request.form["domicile"])

                break

        return redirect("/admin")

    # Lecture Google Sheets
    m = get_match_google(i)

    if not m:
        return "Match introuvable"
=======
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
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return render_template(
        "edit.html",
        m=m,
        equipes=EQUIPES
    )

@app.route("/confirm_reset/<int:i>")
def confirm_reset(i):

    if not session.get("admin"):
        return redirect("/login")

<<<<<<< HEAD
    match = get_match_google(i)

    if not match:
        return "Match introuvable"
=======
    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs WHERE id=?",
        (i,)
    )

    match = cur.fetchone()

    c.close()
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return render_template(
        "confirmation_reset.html",
        match=match
    )
<<<<<<< HEAD

=======
    
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
@app.route("/reset_match/<int:i>")
def reset_match(i):

    if not session.get("admin"):
        return redirect("/login")

<<<<<<< HEAD
    # Remise à zéro du match
    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(
        lignes[1:],
        start=2
    ):

        if row[0] == str(i):

            # Statut
            sheet_matchs.update_cell(
                index,
                9,
                "Avant match"
            )

            # Score ASLM
            sheet_matchs.update_cell(
                index,
                10,
                0
            )

            # Score ADV
            sheet_matchs.update_cell(
                index,
                11,
                0
            )
            # heure_debut
            sheet_matchs.update_cell(
                index,
                13,
                ""
            )

            # minute_match
            sheet_matchs.update_cell(
                index,
                14,
                0
            )

            # periode
            sheet_matchs.update_cell(
                index,
                15,
                1
            )

            break

    # Suppression des buts du match
    lignes_buts = sheet_buts.get_all_values()

    lignes_a_garder = [lignes_buts[0]]

    for row in lignes_buts[1:]:

        if row[0] != str(i):
            lignes_a_garder.append(row)

    sheet_buts.clear()

    sheet_buts.update(
        "A1",
        lignes_a_garder
    )

    return redirect(f"/match/{i}")

=======
    c = db()
    cur = c.cursor()

    # Remise à zéro du match
    cur.execute(
        """
        UPDATE matchs
        SET score_aslm = 0,
            score_adv = 0,
            statut = 'Avant match'
        WHERE id = ?
        """,
        (i,)
    )

    # Suppression des buteurs
    cur.execute(
        """
        DELETE FROM buts
        WHERE match_id = ?
        """,
        (i,)
    )

    c.commit()
    c.close()

    return redirect(f"/match/{i}")
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

@app.route("/confirm_delete/<int:i>")
def confirm_delete(i):

    if not session.get("admin"):
        return redirect("/login")

<<<<<<< HEAD
    match = get_match_google(i)

    if not match:
        return "Match introuvable"
=======
    c = db()
    cur = c.cursor()

    cur.execute(
        "SELECT * FROM matchs WHERE id=?",
        (i,)
    )

    match = cur.fetchone()

    c.close()
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return render_template(
        "confirmation.html",
        match=match
    )
  
@app.route("/delete/<int:i>")
def delete(i):

<<<<<<< HEAD
    if not session.get("admin"):
        return redirect("/login")

    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(
        lignes[1:],
        start=2
    ):

        if row[0] == str(i):

            sheet_matchs.update_cell(
                index,
                12,
                "NON"
            )

            break
=======
    c = db()
    cur = c.cursor()

    cur.execute(
        "DELETE FROM matchs WHERE id=?",
        (i,)
    )

    c.commit()
    c.close()
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return redirect("/admin")


@app.route("/match/<int:i>")
def match(i):

<<<<<<< HEAD
    if not session.get("admin"):
        return redirect("/login")

    m = get_match_google(i)

    if not m:
        return "Match introuvable"
=======
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
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    joueurs_compo = []

    try:

        equipe = m[1]
<<<<<<< HEAD
        date_match = m[3]
=======
        date_match = m[5]
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

        joueurs_compo = get_joueurs_match(
            equipe,
            date_match
        )

<<<<<<< HEAD
=======
        print("================================")
        print("Equipe :", equipe)
        print("Date :", date_match)
        print("JOUEURS TROUVES :", joueurs_compo)
        print("================================")

>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
    except Exception as e:

        print("Erreur :", e)

<<<<<<< HEAD
    buts = get_buts_google(i)
    
    minute_match = calcul_minute_match(m)
    
    print("MINUTE MATCH =", minute_match)

    return render_template(
        "match.html",
        match=m,
        buts=buts,
        joueurs_compo=joueurs_compo,
        minute_match=minute_match
    )

@app.route("/statut/<int:i>/<path:s>")
def statut(i, s):

    if not session.get("admin"):
        return redirect("/login")

    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(
        lignes[1:],
        start=2
    ):

        if row[0] == str(i):

            # Colonne I = statut
            sheet_matchs.update_cell(
                index,
                9,
                s
            )
            
            if s == "Terminé":

                match = row

                minute_finale = calcul_minute_match(match)

                # minute_match
                sheet_matchs.update_cell(
                    index,
                    14,
                    minute_finale
                )

            
            if s == "Avant match":

                # heure_debut
                sheet_matchs.update_cell(
                    index,
                    13,
                    ""
                )

                # minute_match
                sheet_matchs.update_cell(
                    index,
                    14,
                    0
                )

                # periode
                sheet_matchs.update_cell(
                    index,
                    15,
                    1
                )
        
            break

    return redirect(f"/match/{i}")
=======
    return render_template(
        "match.html",
        match=m,
        buts=b,
        joueurs_compo=joueurs_compo
    )

>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

@app.route("/score/<int:i>/<t>")
def score(i, t):

<<<<<<< HEAD
    if not session.get("admin"):
        return redirect("/login")

    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(
        lignes[1:],
        start=2
    ):

        if row[0] == str(i):

            score_aslm = int(row[9])
            score_adv = int(row[10])

            # + ASLM
            if t == "pa":
                score_aslm += 1

            # - ASLM
            elif t == "ma":
                score_aslm = max(
                    score_aslm - 1,
                    0
                )

            # + ADV
            elif t == "pv":
                score_adv += 1

            # - ADV
            elif t == "mv":
                score_adv = max(
                    score_adv - 1,
                    0
                )

            # Colonne J = score ASLM
            sheet_matchs.update_cell(
                index,
                10,
                score_aslm
            )

            # Colonne K = score ADV
            sheet_matchs.update_cell(
                index,
                11,
                score_adv
            )

            break

    return redirect(f"/match/{i}")

@app.route("/but/<int:i>", methods=["POST"])
def but(i):

    if not session.get("admin"):
        return redirect("/login")

=======
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

>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df
    buteur = request.form["buteur"]

    if buteur == "AUTRE":
        buteur = request.form["autre_joueur"]

<<<<<<< HEAD
    # Ajout du but
    ajouter_but_google(
        i,
        request.form["minute"],
        buteur
    )

    # Mise à jour du score ASLM
    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(lignes[1:], start=2):

        if row[0] == str(i):

            score_aslm = int(row[9]) + 1

            sheet_matchs.update_cell(
                index,
                10,   # colonne J = score_aslm
                score_aslm
            )

            break
=======
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
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return redirect(f"/match/{i}")


@app.route("/buteurs")
def buteurs():

<<<<<<< HEAD
    lignes = sheet_buts.get_all_values()

    classement = {}

    for row in lignes[1:]:

        if len(row) < 3:
            continue

        buteur = row[2]

        classement[buteur] = (
            classement.get(buteur, 0) + 1
        )

    rows = sorted(
        classement.items(),
        key=lambda x: x[1],
        reverse=True
    )
=======
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
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

    return render_template(
        "buteurs.html",
        rows=rows
    )
<<<<<<< HEAD
    
@app.route("/mitemps/<int:i>")
def mitemps(i):

    if not session.get("admin"):
        return redirect("/login")

    lignes = sheet_matchs.get_all_values()

    for index, row in enumerate(lignes[1:], start=2):

        if row[0] == str(i):

            # Statut
            sheet_matchs.update_cell(
                index,
                9,
                "Mi-temps"
            )

            # Minute atteinte
            sheet_matchs.update_cell(
                index,
                14,
                45
            )

            # Période 2 prête
            sheet_matchs.update_cell(
                index,
                15,
                2
            )

            break

    return redirect(f"/match/{i}")
=======

print("APP CHARGEE")
>>>>>>> 435aa70cba8373852ece083d67e9e3e72e0b05df

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )