
import os
import csv
import requests
import io
import json

os.makedirs('dati', exist_ok=True)

# Mappatura leghe con codici ufficiali Football-Data.co.uk (Stagione 2026/2027)
LEAGUES = {
    "serie_a": {"nome": "Serie A", "code": "I1"},
    "premier_league": {"nome": "Premier League", "code": "E0"},
    "la_liga": {"nome": "La Liga", "code": "SP1"},
    "bundesliga": {"nome": "Bundesliga", "code": "D1"},
    "ligue_1": {"nome": "Ligue 1", "code": "F1"},
    "olanda": {"nome": "Eredivisie", "code": "N1"},
    "belgio": {"nome": "Pro League", "code": "B1"},
    "turchia": {"nome": "Süper Lig", "code": "T1"}
}

season = "2627"
dati_finali = {}

for key, info in LEAGUES.items():
    url = f"https://www.football-data.co.uk/mmz425/{season}/{info['code']}.csv"
    dati_finali[key] = {"nome_lega": info["nome"], "squadre": {}}
    team_stats = {}

    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            decoded_content = res.content.decode('utf-8', errors='ignore')
            reader = csv.DictReader(io.StringIO(decoded_content))
            
            for row in reader:
                # Normalizza le chiavi rimuovendo spazi e maiuscole
                r = {k.strip().upper(): v.strip() for k, v in row.items() if k}
                
                home = r.get('HOMETEAM', '')
                away = r.get('AWAYTEAM', '')
                if not home or not away:
                    continue
                
                try:
                    fthg = float(r.get('FTHG', 0) or 0)
                    ftag = float(r.get('FTAG', 0) or 0)
                    hst = float(r.get('HST', 0) or 0)   # Home Shots on Target
                    ast = float(r.get('AST', 0) or 0)   # Away Shots on Target
                    hc = float(r.get('HC', 0) or 0)     # Home Corners
                    ac = float(r.get('AC', 0) or 0)     # Away Corners
                    hy = float(r.get('HY', 0) or 0)     # Home Yellow Cards
                    ay = float(r.get('AY', 0) or 0)     # Away Yellow Cards
                except ValueError:
                    continue

                if home not in team_stats:
                    team_stats[home] = {'p_casa': 0, 'gf_c': 0, 'gs_c': 0, 'tiri_f_c': 0, 'tiri_s_c': 0, 'corn_f_c': 0, 'corn_s_c': 0, 'cart_f_c': 0, 'cart_s_c': 0,
                                        'p_fuori': 0, 'gf_f': 0, 'gs_f': 0, 'tiri_f_f': 0, 'tiri_s_f': 0, 'corn_f_f': 0, 'corn_s_f': 0, 'cart_f_f': 0, 'cart_s_f': 0}
                if away not in team_stats:
                    team_stats[away] = {'p_casa': 0, 'gf_c': 0, 'gs_c': 0, 'tiri_f_c': 0, 'tiri_s_c': 0, 'corn_f_c': 0, 'corn_s_c': 0, 'cart_f_c': 0, 'cart_s_c': 0,
                                        'p_fuori': 0, 'gf_f': 0, 'gs_f': 0, 'tiri_f_f': 0, 'tiri_s_f': 0, 'corn_f_f': 0, 'corn_s_f': 0, 'cart_f_f': 0, 'cart_s_f': 0}

                # Statistiche Casa
                ts_h = team_stats[home]
                ts_h['p_casa'] += 1
                ts_h['gf_c'] += fthg
                ts_h['gs_c'] += ftag
                ts_h['tiri_f_c'] += hst
                ts_h['tiri_s_c'] += ast
                ts_h['corn_f_c'] += hc
                ts_h['corn_s_c'] += ac
                ts_h['cart_f_c'] += hy
                ts_h['cart_s_c'] += ay

                # Statistiche Trasferta
                ts_a = team_stats[away]
                ts_a['p_fuori'] += 1
                ts_a['gf_f'] += ftag
                ts_a['gs_f'] += fthg
                ts_a['tiri_f_f'] += ast
                ts_a['tiri_s_f'] += hst
                ts_a['corn_f_f'] += ac
                ts_a['corn_s_f'] += hc
                ts_a['cart_f_f'] += ay
                ts_a['cart_s_f'] += hy

            for team, d in team_stats.items():
                pc = d['p_casa'] or 1
                pf = d['p_fuori'] or 1
                tot_p = d['p_casa'] + d['p_fuori']

                dati_finali[key]["squadre"][team] = {
                    "partita_giocate": tot_p,
                    "casa": {
                        "gf": round(d['gf_c'] / pc, 2),
                        "gs": round(d['gs_c'] / pc, 2),
                        "tiri_fatti": round(d['tiri_f_c'] / pc, 2),
                        "tiri_subiti": round(d['tiri_s_c'] / pc, 2),
                        "corner_fatti": round(d['corn_f_c'] / pc, 2),
                        "corner_concessi": round(d['corn_s_c'] / pc, 2),
                        "cartellini_fatti": round(d['cart_f_c'] / pc, 2),
                        "cartellini_subiti": round(d['cart_s_c'] / pc, 2)
                    },
                    "fuori": {
                        "gf": round(d['gf_f'] / pf, 2),
                        "gs": round(d['gs_f'] / pf, 2),
                        "tiri_fatti": round(d['tiri_f_f'] / pf, 2),
                        "tiri_subiti": round(d['tiri_s_f'] / pf, 2),
                        "corner_fatti": round(d['corn_f_f'] / pf, 2),
                        "corner_concessi": round(d['corn_s_f'] / pf, 2),
                        "cartellini_fatti": round(d['cart_f_f'] / pf, 2),
                        "cartellini_subiti": round(d['cart_s_f'] / pf, 2)
                    }
                }
    except Exception as e:
        print(f"Errore scraping {info['nome']}: {e}")

with open('dati/stats.json', 'w', encoding='utf-8') as f:
    json.dump(dati_finali, f, ensure_ascii=False, indent=4)

print("Scraping CSV completato con dati reali!")
