import csv
import json
import random
import base64
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring, indent
from datetime import date, timedelta

# --- CONFIG ---
folder = Path(__file__).parent
nombres_file = folder / "nombres.csv"
nombres_mujer_file = folder / "nombres_mujer.csv"
apellidos_file = folder / "apellidos.csv"
photos_folder = folder / "photos"
clubs_json_file = folder / "clubes.json"
output_demo = folder / "demo.xml"

num_nadadors = 500
num_campionats = 5
sessions_per_campionat = (2, 4)  # min, max sessions per championship
proves_per_sessio = (3, 6)       # min, max events per session

# --- CARGAR DATOS ---
def load_csv(file):
    with open(file, newline='', encoding='utf-8') as f:
        return [row[0] for row in csv.reader(f)]

nombres_hombre = load_csv(nombres_file)
nombres_mujer = load_csv(nombres_mujer_file)
apellidos = load_csv(apellidos_file)
photos = [p for p in photos_folder.iterdir() if p.is_file()]

with open(clubs_json_file, encoding='utf-8') as f:
    clubs_data = json.load(f)

# --- BUILD XML TREE ---
root = Element('odoo')
data = SubElement(root, 'data')

# --- CREAR CLUBS ---
num_clubs = len(clubs_data)
for i, club in enumerate(clubs_data):
    rec = SubElement(data, 'record', id=f'club_{i+1}', model='natacio.club')
    f_name = SubElement(rec, 'field', name='name')
    f_name.text = str(club["club"])
    f_poble = SubElement(rec, 'field', name='poble')
    f_poble.text = str(club["location"])
    f_socis = SubElement(rec, 'field', name='num_socis')
    f_socis.text = str(random.randint(20, 100))

# --- CREAR CATEGORIAS ---
categorias = [("Infantil", 10, 14), ("Junior", 15, 17), ("Senior", 18, 25)]
num_categorias = len(categorias)
for i, (name, min_edat, max_edat) in enumerate(categorias):
    rec = SubElement(data, 'record', id=f'categoria_{i+1}', model='natacio.categoria')
    f_name = SubElement(rec, 'field', name='name')
    f_name.text = name
    f_min = SubElement(rec, 'field', name='edat_minima')
    f_min.text = str(min_edat)
    f_max = SubElement(rec, 'field', name='edat_maxima')
    f_max.text = str(max_edat)

# --- CREAR ESTILS ---
estils = ["Crol", "Esquena", "Brasa", "Papallona"]
num_estils = len(estils)
for i, estil_name in enumerate(estils):
    rec = SubElement(data, 'record', id=f'estil_{i+1}', model='natacio.estil')
    f_name = SubElement(rec, 'field', name='name')
    f_name.text = estil_name

# --- CREAR NADADORS ---
for i in range(num_nadadors):
    sexo = random.choice(["M", "F"])
    nombre = random.choice(nombres_hombre if sexo == "M" else nombres_mujer)
    apellido = random.choice(apellidos)
    full_name = f"{nombre} {apellido}"
    any_naixement = random.randint(2005, 2015)
    club_id = f"club_{random.randint(1, num_clubs)}"
    categoria_id = f"categoria_{random.randint(1, num_categorias)}"

    rec = SubElement(data, 'record', id=f'nadador_{i+1}', model='natacio.nadador')
    f_name = SubElement(rec, 'field', name='name')
    f_name.text = full_name
    f_nadador = SubElement(rec, 'field', name='es_nadador')
    f_nadador.text = 'True'
    f_any = SubElement(rec, 'field', name='any_naixement')
    f_any.text = str(any_naixement)
    SubElement(rec, 'field', name='categoria_id', ref=categoria_id)
    SubElement(rec, 'field', name='club_id', ref=club_id)

    # Foto
    foto_path = random.choice(photos) if photos else None
    if foto_path:
        with open(foto_path, "rb") as fp:
            foto_b64 = base64.b64encode(fp.read()).decode("utf-8")
            f_foto = SubElement(rec, 'field', name='foto')
            f_foto.text = foto_b64

    f_pag = SubElement(rec, 'field', name='data_ultim_pagament')
    f_pag.text = f"2025-{random.randint(1,12):02d}-{random.randint(1, 28):02d}"

# --- CREAR CAMPIONATS ---
campionat_names = [
    "Campionat Provincial de València",
    "Trofeu Ciutat d'Alacant",
    "Campionat Autonòmic d'Estiu",
    "Copa Federació Hivern",
    "Campionat Interclubs Primavera",
    "Trofeu Mare Nostrum",
    "Open Internacional de Castelló",
    "Campionat Absolut de la Comunitat",
]
random.shuffle(campionat_names)

sessio_counter = 0
prova_counter = 0

for c in range(num_campionats):
    camp_name = campionat_names[c % len(campionat_names)]
    # Random start date in 2025
    start_offset = random.randint(0, 300)
    data_inici = date(2025, 1, 1) + timedelta(days=start_offset)
    num_sessions = random.randint(*sessions_per_campionat)
    data_fi = data_inici + timedelta(days=num_sessions - 1)

    # Select random clubs participating (3-8 clubs)
    participating_clubs = random.sample(range(1, num_clubs + 1), min(random.randint(3, 8), num_clubs))
    # Select random nadadors inscribed (10-30 swimmers)
    inscribed_nadadors = random.sample(range(1, num_nadadors + 1), min(random.randint(10, 30), num_nadadors))

    camp_id = f'campionat_{c+1}'
    rec = SubElement(data, 'record', id=camp_id, model='natacio.campionat')
    f_name = SubElement(rec, 'field', name='name')
    f_name.text = camp_name
    f_inici = SubElement(rec, 'field', name='data_inici')
    f_inici.text = str(data_inici)
    f_fi = SubElement(rec, 'field', name='data_fi')
    f_fi.text = str(data_fi)

    # Many2many clubs: eval="[(6, 0, [ref('club_1'), ref('club_2'), ...])]"
    club_refs = ", ".join([f"ref('club_{cid}')" for cid in participating_clubs])
    f_clubs = SubElement(rec, 'field', name='club_ids', eval=f"[(6, 0, [{club_refs}])]")

    # Many2many nadadors inscrits
    nad_refs = ", ".join([f"ref('nadador_{nid}')" for nid in inscribed_nadadors])
    f_nads = SubElement(rec, 'field', name='nadadors_inscrits_ids', eval=f"[(6, 0, [{nad_refs}])]")

    # --- CREAR SESSIONS per campionat ---
    for s in range(num_sessions):
        sessio_counter += 1
        sessio_id = f'sessio_{sessio_counter}'
        sessio_date = data_inici + timedelta(days=s)

        # Subset of inscribed swimmers for this session
        sessio_nadadors = random.sample(inscribed_nadadors, min(random.randint(6, 20), len(inscribed_nadadors)))

        rec_s = SubElement(data, 'record', id=sessio_id, model='natacio.sessio')
        f_data = SubElement(rec_s, 'field', name='data')
        f_data.text = str(sessio_date)
        SubElement(rec_s, 'field', name='campionat_id', ref=camp_id)

        # Many2many nadadors in session
        sess_nad_refs = ", ".join([f"ref('nadador_{nid}')" for nid in sessio_nadadors])
        SubElement(rec_s, 'field', name='nadadors_ids', eval=f"[(6, 0, [{sess_nad_refs}])]")

        # --- CREAR PROVES per sessio ---
        num_proves = random.randint(*proves_per_sessio)
        distancies = [50, 100, 200, 400]
        for p in range(num_proves):
            prova_counter += 1
            prova_id = f'prova_{prova_counter}'
            estil_idx = random.randint(1, num_estils)
            cat_idx = random.randint(1, num_categorias)
            distancia = random.choice(distancies)
            estil_nom = estils[estil_idx - 1]
            cat_nom = categorias[cat_idx - 1][0]

            # Subset of session swimmers for this event
            prova_nadadors = random.sample(sessio_nadadors, min(random.randint(3, 8), len(sessio_nadadors)))

            rec_p = SubElement(data, 'record', id=prova_id, model='natacio.prova')
            f_desc = SubElement(rec_p, 'field', name='descripcio')
            f_desc.text = f"{distancia}m {estil_nom} - {cat_nom}"
            SubElement(rec_p, 'field', name='estil_id', ref=f'estil_{estil_idx}')
            SubElement(rec_p, 'field', name='categoria_id', ref=f'categoria_{cat_idx}')
            SubElement(rec_p, 'field', name='sessio_id', ref=sessio_id)

            # Many2many nadadors in prova
            prova_nad_refs = ", ".join([f"ref('nadador_{nid}')" for nid in prova_nadadors])
            SubElement(rec_p, 'field', name='nadadors_ids', eval=f"[(6, 0, [{prova_nad_refs}])]")

# --- GUARDAR DEMO.XML ---
indent(root, space='    ')
xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding='unicode')
with open(output_demo, "w", encoding="utf-8") as f:
    f.write(xml_str)

print(f"Demo XML generado en: {output_demo}")
print(f"  - {num_clubs} clubs")
print(f"  - {num_categorias} categorias")
print(f"  - {num_estils} estils")
print(f"  - {num_nadadors} nadadors")
print(f"  - {num_campionats} campionats")
print(f"  - {sessio_counter} sessions")
print(f"  - {prova_counter} proves")