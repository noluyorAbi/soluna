import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
from adjustText import adjust_text
import coc
import asyncio
import plotly.express as px
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Schriftart anpassen, um fehlende Glyphen zu vermeiden
plt.rcParams['font.family'] = 'DejaVu Sans'  # 'DejaVu Sans' ist standardmäßig in matplotlib enthalten

# dotenv laden
load_dotenv()

# Clash of Clans API E-Mail und Passwort aus .env laden
COC_EMAIL = os.getenv('COC_EMAIL')
COC_PASSWORD = os.getenv('COC_PASSWORD')
CLAN_TAG = '#2LUVL2QGL'  # Ersetzen Sie dies mit Ihrem Clan-Tag

# Gewichtungsfaktoren einstellen (können nach Bedarf angepasst werden)
DONATION_WEIGHT = 1.0          # Gewichtung für Spenden Gegeben
DONATION_RECEIVED_WEIGHT = 0.5 # Gewichtung für Spenden Erhalten
ATTACK_WIN_WEIGHT = 1.5        # Basisgewichtung für gewonnene Angriffe
TROPHY_SCALE = 1000.0          # Skalierungsfaktor für Trophäen
ATTACK_BASE_WEIGHT = 1.0       # Basisgewichtungsfaktor zusätzlich zum Skalierungsfaktor

# FastAPI-App initialisieren
app = FastAPI()

origins = [
    "http://localhost:3000",  # Port Ihres Next.js-Entwicklungsservers
    # Fügen Sie weitere Ursprünge hinzu, wenn nötig
]

# CORS erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # In der Produktion sollten Sie dies auf Ihre Domäne beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_clan_members(clan_tag, coc_client):
    """
    Ruft die Mitglieder eines Clans anhand des Clan-Tags ab.
    """
    try:
        clan = await coc_client.get_clan(clan_tag)
        members = clan.members
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erfolgreich Clan-Mitglieder abgerufen: {len(members)} Mitglieder gefunden.")
        return members
    except coc.NotFound as not_found_err:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Clan nicht gefunden: {not_found_err}")
    except Exception as err:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ein Fehler ist aufgetreten beim Abrufen der Clan-Mitglieder: {err}")
    return []

async def get_player_data(player_tag, coc_client):
    """
    Ruft die Daten eines Spielers anhand des Spieler-Tags ab.
    """
    try:
        player = await coc_client.get_player(player_tag)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erfolgreich Daten für Spieler {player.name} abgerufen.")
        return {
            'name': player.name,
            'trophies': player.trophies,
            'donations': player.donations,
            'donationsReceived': player.received,
            'attackWins': player.attack_wins
        }
    except coc.NotFound as not_found_err:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Spieler nicht gefunden: {not_found_err}")
    except Exception as err:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ein Fehler ist aufgetreten beim Abrufen von Spieler {player_tag}: {err}")
    return None

def create_interactive_activity_plot(members_data, donation_weight=1.0, donation_received_weight=0.5,
                                     attack_win_weight=1.5, trophy_scale=1000.0, attack_base_weight=1.0):
    """
    Erstellt einen interaktiven Scatter Plot mit Plotly und gibt den HTML-Code zurück.
    """
    # Erstellen eines DataFrame mit den relevanten Daten
    df = pd.DataFrame(members_data)

    # Überprüfen, ob der DataFrame leer ist
    if df.empty:
        print("Keine Daten zum Plotten verfügbar.")
        return "<p>Keine Daten zum Plotten verfügbar.</p>"

    # Gewichtung der gewonnenen Angriffe basierend auf Trophäen
    df['attackWinWeight'] = attack_base_weight + (df['trophies'] / trophy_scale)

    # Berechnung der Aktivität unter Berücksichtigung der Spenden erhalten
    df['Aktivität'] = (df['donations'] * donation_weight) + \
                      (df['donationsReceived'] * donation_received_weight) + \
                      (df['attackWins'] * df['attackWinWeight'])

    # Spieler nach Aktivität sortieren und eine eindeutige ID zuweisen
    df = df.sort_values(by='Aktivität', ascending=False).reset_index(drop=True)
    df['Spieler_ID'] = df.index + 1  # Startet bei 1

    # Quantile berechnen (z.B. 25%, 50%, 75%)
    quantiles = df['Aktivität'].quantile([0.25, 0.5, 0.75]).tolist()

    def assign_quantile(value):
        if value <= quantiles[0]:
            return 'Unteres 25%'
        elif value <= quantiles[1]:
            return 'Mittleres 50%'
        elif value <= quantiles[2]:
            return 'Oberes 25%'
        else:
            return 'Sehr hoch'

    df['Quantil'] = df['Aktivität'].apply(assign_quantile)

    # Farben für Quantile definieren
    quantil_colors = {
        'Unteres 25%': 'red',
        'Mittleres 50%': 'orange',
        'Oberes 25%': 'green',
        'Sehr hoch': 'blue'  # Optional, falls vorhanden
    }

    # Interaktiven Plot erstellen
    fig = px.scatter(
        df,
        x='Spieler_ID',
        y='Aktivität',
        color='Quantil',
        color_discrete_map=quantil_colors,
        hover_data=['name', 'trophies', 'donations', 'donationsReceived', 'attackWins'],
        labels={
            'Spieler_ID': 'Spieler ID',
            'Aktivität': 'Aktivität'
        },
        title='Clan-Mitglieder Aktivitäts-Plot'
    )

    # Plot als HTML-String erhalten, Höhe auf 600px festlegen
    plot_div = fig.to_html(include_plotlyjs='cdn', full_html=False, default_height='600px')

    # Erklärungstext für die HTML-Datei erstellen
    explanation_text = (
    "<style>"
    "body { font-family: Arial, sans-serif; margin: 20px; }"
    "h2, h3 { color: #2E75B6; }"
    "p, ul, ol { font-size: 1.1em; }"
    "ul, ol { margin-left: 20px; }"
    "ul { list-style-type: square; }"
    "table { border-collapse: collapse; width: 100%; margin-top: 20px; }"
    "th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }"
    "th { background-color: #2E75B6; color: white; }"
    "</style>"
    "<h2>Erklärung zur Aktivitätsberechnung</h2>"
    "<p>Die Aktivität jedes Clan-Mitglieds wird mit der folgenden Formel berechnet:</p>"
    "<p><strong>Aktivität = (Spenden Gegeben × Gewichtung) + "
    "(Spenden Erhalten × Gewichtung) + "
    "(Gewonnene Angriffe × (Basisgewichtung + Trophäen / Skalierungsfaktor))</strong></p>"

    "<h3>Gewichtungsfaktoren:</h3>"
    "<table>"
    "<tr><th>Faktor</th><th>Wert</th></tr>"
    f"<tr><td>Spenden Gegeben</td><td>{donation_weight}</td></tr>"
    f"<tr><td>Spenden Erhalten</td><td>{donation_received_weight}</td></tr>"
    f"<tr><td>Gewonnene Angriffe</td><td>{attack_base_weight} + (Trophäen / {trophy_scale})</td></tr>"
    "</table>"

    "<h3>Interpretation:</h3>"
    "<p>Dieser Aktivitätsindex kombiniert verschiedene Faktoren, die die Aktivität und Beiträge eines Spielers innerhalb des Clans widerspiegeln:</p>"
    "<ul>"
    "<li><strong>Spenden Gegeben:</strong> Zeigt die Bereitschaft eines Spielers an, anderen Clanmitgliedern zu helfen.</li>"
    "<li><strong>Spenden Erhalten:</strong> Indiziert die Interaktion des Spielers mit dem Clan, hat jedoch eine geringere Gewichtung.</li>"
    "<li><strong>Gewonnene Angriffe:</strong> Reflektiert die Kampfaktivität und den Erfolg des Spielers. Die Gewichtung wird durch die Trophäenanzahl beeinflusst, um das Spielniveau zu berücksichtigen.</li>"
    "</ul>"
    "<p>Die Trophäenanzahl dient als Indikator für das Spielniveau. Höhere Trophäen bedeuten, dass der Spieler auf einem höheren Wettbewerbsniveau spielt, was bei der Berechnung der Aktivität berücksichtigt wird.</p>"

    "<h3>Beispielberechnung:</h3>"
    "<p>Angenommen, ein Spieler hat folgende Statistiken:</p>"
    "<ul>"
    "<li>Spenden Gegeben: 120</li>"
    "<li>Spenden Erhalten: 80</li>"
    "<li>Gewonnene Angriffe: 150</li>"
    "<li>Trophäen: 2000</li>"
    "</ul>"
    "<p>Die Berechnung der Aktivität wäre dann:</p>"
    "<p>"
    f"Aktivität = (120 × {donation_weight}) + "
    f"(80 × {donation_received_weight}) + "
    f"(150 × ({attack_base_weight} + 2000 / {trophy_scale}))"
    "</p>"
    "<h4>Schrittweise Berechnung:</h4>"
    "<ol>"
    f"<li>Spenden Gegeben Beitrag: 120 × {donation_weight} = {120 * donation_weight}</li>"
    f"<li>Spenden Erhalten Beitrag: 80 × {donation_received_weight} = {80 * donation_received_weight}</li>"
    f"<li>Gewonnene Angriffe Gewichtung: {attack_base_weight} + 2000 / {trophy_scale} = {attack_base_weight + 2000 / trophy_scale}</li>"
    f"<li>Gewonnene Angriffe Beitrag: 150 × ({attack_base_weight + 2000 / trophy_scale}) = {150 * (attack_base_weight + 2000 / trophy_scale)}</li>"
    "<li>Gesamtaktivität: Summe aller Beiträge</li>"
    "</ol>"
    "<p>Dies ergibt den endgültigen Aktivitätswert, der zum Vergleich der Clan-Mitglieder verwendet werden kann.</p>"
)

    # Gesamtes HTML erstellen
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Clan-Mitglieder Aktivitäts-Plot</title>
    </head>
    <body>
        {plot_div}
        {explanation_text}
    </body>
    </html>
    """

    return full_html

# FastAPI-Endpunkt definieren
@app.get("/clan-activity")
async def clan_activity():
    """
    Hauptfunktion, die den Workflow steuert und das Ergebnis als HTML zurückgibt.
    """
    # Überprüfen, ob E-Mail und Passwort gesetzt sind
    if not COC_EMAIL or not COC_PASSWORD:
        return HTMLResponse(content="COC_EMAIL oder COC_PASSWORD ist nicht gesetzt. Bitte überprüfen Sie Ihre .env-Datei.", status_code=500)

    # coc.py Client initialisieren
    async with coc.Client() as coc_client:
        try:
            await coc_client.login(COC_EMAIL, COC_PASSWORD)
        except coc.InvalidCredentials as error:
            return HTMLResponse(content=f"Ungültige Anmeldedaten: {error}", status_code=500)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Start der Datenabfrage...")
        members = await get_clan_members(CLAN_TAG, coc_client)

        if not members:
            return HTMLResponse(content="Keine Mitgliederinformationen abgerufen. Beende das Programm.", status_code=500)

        # Für jedes Mitglied die zusätzlichen Daten abrufen
        tasks = [get_player_data(member.tag, coc_client) for member in members]
        player_data_list = await asyncio.gather(*tasks, return_exceptions=True)

        detailed_members = []
        for data in player_data_list:
            if data is not None and not isinstance(data, Exception):
                detailed_members.append(data)
            else:
                # Falls keine Daten abgerufen werden konnten
                detailed_members.append({
                    'name': 'Unbekannt',
                    'trophies': 0,
                    'donations': 0,
                    'donationsReceived': 0,
                    'attackWins': 0
                })

        print("\nErstelle den interaktiven Plot mit Plotly...")
        html_content = create_interactive_activity_plot(
            detailed_members,
            donation_weight=DONATION_WEIGHT,
            donation_received_weight=DONATION_RECEIVED_WEIGHT,
            attack_win_weight=ATTACK_WIN_WEIGHT,
            trophy_scale=TROPHY_SCALE,
            attack_base_weight=ATTACK_BASE_WEIGHT
        )
        print("Interaktiver Plot erfolgreich erstellt.")

        return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
