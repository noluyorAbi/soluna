import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import coc
import asyncio
import plotly.express as px
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import html  # Für HTML-Escaping
from mangum import Mangum  # Importiere Mangum für die Integration mit Vercel

# Schriftart anpassen, um fehlende Glyphen zu vermeiden
plt.rcParams['font.family'] = 'DejaVu Sans'  # 'DejaVu Sans' ist standardmäßig in matplotlib enthalten

# dotenv laden (nur lokal nützlich, Vercel verwendet Environment Variables)
load_dotenv()

# Clash of Clans API E-Mail und Passwort aus Environment Variables laden
COC_EMAIL = os.getenv('COC_EMAIL')
COC_PASSWORD = os.getenv('COC_PASSWORD')
CLAN_TAG = '#2LUVL2QGL'  # Ersetzen Sie dies mit Ihrem Clan-Tag

# Gewichtungsfaktoren einstellen (können nach Bedarf angepasst werden)
DONATION_WEIGHT = 1.0           # Gewichtung für Spenden Gegeben
DONATION_RECEIVED_WEIGHT = 0.5  # Gewichtung für Spenden Erhalten
ATTACK_WIN_WEIGHT = 1.5         # Basisgewichtung für gewonnene Angriffe
TROPHY_SCALE = 1000.0           # Skalierungsfaktor für Trophäen
ATTACK_BASE_WEIGHT = 1.0        # Basisgewichtungsfaktor zusätzlich zum Skalierungsfaktor

# FastAPI-App initialisieren
app = FastAPI()

origins = [
    "http://localhost:3000",  # Port Ihres Next.js-Entwicklungsservers
    "https://soluna-nine.vercel.app",# Fügen Sie weitere Ursprünge hinzu, wenn nötig
    "https://soluna-production.up.railway.app", # Produktionsfrontend
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

def generate_html_table(dataframe, title, table_id):
    table_html = f"<h3>{html.escape(title)}</h3><table id='{html.escape(table_id)}'>"
    # Kopfzeile mit zusätzlichen Spalten
    table_html += (
        "<thead>"
        "<tr>"
        "<th>Rang</th>"
        "<th>Name</th>"
        "<th>Aktivität</th>"
        "<th>Trophäen</th>"
        "<th>Spenden Gegeben</th>"
        "<th>Spenden Erhalten</th>"
        "<th>Gewonnene Angriffe</th>"
        "<th>Spenden Verhältnis</th>"
        "</tr>"
        "</thead><tbody>"
    )
    for index, row in dataframe.iterrows():
        spenden_verhältnis = row['Spenden_Verhältnis']
        # Versuchen, den Spenden-Verhältnis-Wert in eine Zahl umzuwandeln
        try:
            ratio = float(spenden_verhältnis)
            if ratio > 1:
                color = "green"
            elif ratio < 1:
                color = "red"
            else:
                color = "black"  # Falls das Verhältnis genau 1 ist
            ratio_html = f"<td style='color: {color};'>{html.escape(str(spenden_verhältnis))}</td>"
        except ValueError:
            # Falls der Wert nicht numerisch ist, keine Farbe anwenden
            ratio_html = f"<td>{html.escape(str(spenden_verhältnis))}</td>"

        table_html += (
            "<tr>"
            f"<td>{index + 1}</td>"
            f"<td>{html.escape(str(row['name']))}</td>"
            f"<td>{row['Aktivität']:.2f}</td>"
            f"<td>{row['trophies']}</td>"
            f"<td>{row['donations']}</td>"
            f"<td>{row['donationsReceived']}</td>"
            f"<td>{row['attackWins']}</td>"
            f"{ratio_html}"
            "</tr>"
        )
    table_html += "</tbody></table>"
    return table_html


def generate_full_html_table(dataframe, title, table_id):
    table_html = f"<h3>{html.escape(title)}</h3><table id='{html.escape(table_id)}'>"
    table_html += (
        "<thead>"
        "<tr>"
        "<th>Rang</th>"
        "<th>Name</th>"
        "<th>Aktivität</th>"
        "<th>Trophäen</th>"
        "<th>Spenden Gegeben</th>"
        "<th>Spenden Erhalten</th>"
        "<th>Gewonnene Angriffe</th>"
        "<th>Spenden Verhältnis</th>"
        "</tr>"
        "</thead><tbody>"
    )
    for index, row in dataframe.iterrows():
        spenden_verhältnis = row['Spenden_Verhältnis']
        # Versuchen, den Spenden-Verhältnis-Wert in eine Zahl umzuwandeln
        try:
            ratio = float(spenden_verhältnis)
            if ratio > 1:
                color = "green"
            elif ratio < 1:
                color = "red"
            else:
                color = "black"  # Falls das Verhältnis genau 1 ist
            ratio_html = f"<td style='color: {color};'>{html.escape(str(spenden_verhältnis))}</td>"
        except ValueError:
            # Falls der Wert nicht numerisch ist, keine Farbe anwenden
            ratio_html = f"<td>{html.escape(str(spenden_verhältnis))}</td>"

        table_html += (
            "<tr>"
            f"<td>{index + 1}</td>"
            f"<td>{html.escape(str(row['name']))}</td>"
            f"<td>{row['Aktivität']:.2f}</td>"
            f"<td>{row['trophies']}</td>"
            f"<td>{row['donations']}</td>"
            f"<td>{row['donationsReceived']}</td>"
            f"<td>{row['attackWins']}</td>"
            f"{ratio_html}"
            "</tr>"
        )
    table_html += "</tbody></table>"
    return table_html


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

    # Sicherstellen, dass alle erforderlichen Spalten vorhanden sind
    required_columns = ['name', 'trophies', 'donations', 'donationsReceived', 'attackWins']
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0  # Setze fehlende Spalten auf 0

    # Gewichtung der gewonnenen Angriffe basierend auf Trophäen
    df['attackWinWeight'] = attack_base_weight + (df['trophies'] / trophy_scale)

    # Berechnung der Aktivität unter Berücksichtigung der Spenden erhalten
    df['Aktivität'] = (df['donations'] * donation_weight) + \
                      (df['donationsReceived'] * donation_received_weight) + \
                      (df['attackWins'] * df['attackWinWeight'])

    # Berechnung des Spenden-Verhältnisses mit spezifischer Fehlerbehandlung
    def calculate_donation_ratio(row):
        donations = row['donations']
        donations_received = row['donationsReceived']
        if donations > 0 and donations_received > 0:
            return f"{donations / donations_received:.2f}"
        elif donations > 0 and donations_received == 0:
            return "Keine erhalten"
        elif donations == 0 and donations_received > 0:
            return "Keine gegeben"
        else:
            return "Keine gegeben & erhalten"

    df['Spenden_Verhältnis'] = df.apply(calculate_donation_ratio, axis=1)

    # Spieler nach Aktivität sortieren und eine eindeutige ID zuweisen
    df = df.sort_values(by='Aktivität', ascending=False).reset_index(drop=True)
    df['Spieler_ID'] = df.index + 1  # Startet bei 1

    # Berechnung der Top 5 und Bottom 5
    top_5 = df.head(5)
    bottom_5 = df.tail(5)

    # Erstellung der HTML-Tabellen für Top 5 und Bottom 5
    top_5_html = generate_html_table(top_5, "Top 5 Aktive Clan-Mitglieder", "top5_table")
    bottom_5_html = generate_html_table(bottom_5, "Bottom 5 Aktive Clan-Mitglieder", "bottom5_table")

    # Erstellung der Haupttabelle mit allen Clan-Mitgliedern
    full_table_html = generate_full_html_table(df, "Alle Clan-Mitglieder", "full_table")

    # Berechnung von Durchschnitt und Median der Aktivität
    mean_activity = df['Aktivität'].mean()
    median_activity = df['Aktivität'].median()

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

    # Interaktiven Scatter Plot erstellen
    fig = px.scatter(
        df,
        x='Spieler_ID',
        y='Aktivität',
        color='Quantil',
        color_discrete_map=quantil_colors,
        custom_data=['name', 'trophies', 'donations', 'donationsReceived', 'attackWins', 'Spenden_Verhältnis'],
        labels={
            'Spieler_ID': 'Spieler ID',
            'Aktivität': 'Aktivität'
        },
        title='Clan-Mitglieder Aktivitäts-Plot'
    )

    # Anpassung des Hover-Templates, damit der Name ganz oben steht
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Trophäen: %{customdata[1]}<br>"
            "Spenden Gegeben: %{customdata[2]}<br>"
            "Spenden Erhalten: %{customdata[3]}<br>"
            "Gewonnene Angriffe: %{customdata[4]}<br>"
            "Spenden Verhältnis: %{customdata[5]}<br>"
            "<extra></extra>"
        )
    )

    # Durchschnittliche Aktivität als separater Trace hinzufügen
    fig.add_trace(
        px.line(
            x=[0, df['Spieler_ID'].max() + 1],
            y=[mean_activity, mean_activity],
            labels={'x': 'Spieler ID', 'y': 'Aktivität'},
            title='Durchschnittliche Aktivität'
        ).update_traces(
            name='Durchschnittliche Aktivität',
            line=dict(color="RoyalBlue", width=2, dash="dash"),
            hoverinfo='skip',
            showlegend=True  # Sicherstellen, dass die Linie in der Legende erscheint
        ).data[0]
    )

    # Median Aktivität als separater Trace hinzufügen
    fig.add_trace(
        px.line(
            x=[0, df['Spieler_ID'].max() + 1],
            y=[median_activity, median_activity],
            labels={'x': 'Spieler ID', 'y': 'Aktivität'},
            title='Median Aktivität'
        ).update_traces(
            name='Median Aktivität',
            line=dict(color="Green", width=2, dash="dot"),
            hoverinfo='skip',
            showlegend=True  # Sicherstellen, dass die Linie in der Legende erscheint
        ).data[0]
    )

    # Hinzufügen von Annotationen für die Linien (optional)
    fig.add_annotation(
        x=df['Spieler_ID'].max(),
        y=mean_activity,
        xref="x",
        yref="y",
        text="Durchschnittliche Aktivität",
        showarrow=True,
        arrowhead=7,
        ax=-40,
        ay=0,
        bgcolor="RoyalBlue",
        font=dict(color="white")
    )

    fig.add_annotation(
        x=df['Spieler_ID'].max(),
        y=median_activity,
        xref="x",
        yref="y",
        text="Median Aktivität",
        showarrow=True,
        arrowhead=7,
        ax=-40,
        ay=0,
        bgcolor="Green",
        font=dict(color="white")
    )

    # Plot als HTML-String erhalten, Höhe auf 600px festlegen
    plot_div = fig.to_html(include_plotlyjs='cdn', full_html=False, default_height='600px')

    # Gesamte HTML-Tabellen (Top 5, Bottom 5 und Haupttabelle)
    full_tables_html = f"""
    <div>
        {top_5_html}
        {bottom_5_html}
        {full_table_html}
    </div>
    """

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
        "<hr><h2>Erklärung zur Aktivitätsberechnung</h2>"
        "<p>Die Aktivität jedes Clan-Mitglieds wird mit der folgenden Formel berechnet:</p>"
        "<p><strong>Aktivität = (Spenden Gegeben × Gewichtung) + "
        "(Spenden Erhalten × Gewichtung) + "
        "(Gewonnene Angriffe × (Basisgewichtung + Trophäen / Skalierungsfaktor))</strong></p>"

        "<h3>Gewichtungsfaktoren:</h3>"
        "<table>"
        "<tr><th>Faktor</th><th>Wert</th></tr>"
        f"<tr><td>Spenden Gegeben</td><td>{DONATION_WEIGHT}</td></tr>"
        f"<tr><td>Spenden Erhalten</td><td>{DONATION_RECEIVED_WEIGHT}</td></tr>"
        f"<tr><td>Gewonnene Angriffe</td><td>{ATTACK_BASE_WEIGHT} + (Trophäen / {TROPHY_SCALE})</td></tr>"
        "</table>"

        "<h3>Spenden Verhältnis:</h3>"
        "<p>Das Spenden-Verhältnis berechnet das Verhältnis von <strong>Spenden Gegeben</strong> zu <strong>Spenden Erhalten</strong>. Ein höheres Verhältnis deutet darauf hin, dass ein Spieler mehr Spenden gibt als erhält, was auf eine unterstützende Rolle im Clan hinweist. Falls ein Spieler keine Spenden gegeben oder erhalten hat, wird dies entsprechend angezeigt:</p>"
        "<ul>"
        "<li><strong>Keine erhalten:</strong> Der Spieler gibt Spenden, erhält jedoch keine.</li>"
        "<li><strong>Keine gegeben:</strong> Der Spieler erhält Spenden, gibt jedoch keine.</li>"
        "<li><strong>Keine gegeben & erhalten:</strong> Der Spieler gibt und erhält keine Spenden.</li>"
        "<li><strong>Verhältniswert:</strong> Das Verhältnis von Spenden Gegeben zu Spenden Erhalten.</li>"
        "</ul>"

        "<h3>Durchschnittliche und Median Aktivität:</h3>"
        "<p>Im Plot sind die durchschnittliche Aktivität (blau gestrichelt) und der Median der Aktivität (grün punktiert) des Clans als horizontale Linien gekennzeichnet. Diese dienen als Referenzpunkte, um die Position der einzelnen Mitglieder im Vergleich zum Durchschnitt und Median des Clans zu sehen.</p>"

        "<h3>Interpretation:</h3>"
        "<p>Dieser Aktivitätsindex kombiniert verschiedene Faktoren, die die Aktivität und Beiträge eines Spielers innerhalb des Clans widerspiegeln:</p>"
        "<ul>"
        "<li><strong>Spenden Gegeben:</strong> Zeigt die Bereitschaft eines Spielers an, anderen Clanmitgliedern zu helfen.</li>"
        "<li><strong>Spenden Erhalten:</strong> Indiziert die Interaktion des Spielers mit dem Clan, hat jedoch eine geringere Gewichtung.</li>"
        "<li><strong>Gewonnene Angriffe:</strong> Reflektiert die Kampfaktivität und den Erfolg des Spielers. Die Gewichtung wird durch die Trophäenanzahl beeinflusst, um das Spielniveau zu berücksichtigen.</li>"
        "</ul>"
        "<p>Die Trophäenanzahl dient als Indikator für das Spielniveau. Höhere Trophäen bedeuten, dass der Spieler auf einem höheren Wettbewerbsniveau spielt, was bei der Berechnung der Aktivität berücksichtigt wird.</p>"

        "<hr>"
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
        f"Aktivität = (120 × {DONATION_WEIGHT}) + "
        f"(80 × {DONATION_RECEIVED_WEIGHT}) + "
        f"(150 × ({ATTACK_BASE_WEIGHT} + 2000 / {TROPHY_SCALE}))"
        "</p>"
        "<h4>Schrittweise Berechnung:</h4>"
        "<ol>"
        f"<li>Spenden Gegeben Beitrag: 120 × {DONATION_WEIGHT} = {120 * DONATION_WEIGHT}</li>"
        f"<li>Spenden Erhalten Beitrag: 80 × {DONATION_RECEIVED_WEIGHT} = {80 * DONATION_RECEIVED_WEIGHT}</li>"
        f"<li>Gewonnene Angriffe Gewichtung: {ATTACK_BASE_WEIGHT} + 2000 / {TROPHY_SCALE} = {ATTACK_BASE_WEIGHT + 2000 / TROPHY_SCALE}</li>"
        f"<li>Gewonnene Angriffe Beitrag: 150 × ({ATTACK_BASE_WEIGHT + 2000 / TROPHY_SCALE}) = {150 * (ATTACK_BASE_WEIGHT + 2000 / TROPHY_SCALE)}</li>"
        f"<li>Spenden Verhältnis: 120 / 80 = 1.50</li>"
        "<li>Gesamtaktivität: Summe aller Beiträge</li>"
        "</ol>"
        "<p>Dies ergibt den endgültigen Aktivitätswert, der zum Vergleich der Clan-Mitglieder verwendet werden kann.</p>"
    )

    # Erfasse den aktuellen Zeitpunkt
    current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    # HTML für den Timestamp erstellen
    timestamp_html = f"<hr><p><em>Daten vom: {current_time}</em></p>"

    # Gesamtes HTML erstellen mit allen Tabellen vor dem Erklärungstext und dem Timestamp
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Clan-Mitglieder Aktivitäts-Plot</title>
        <!-- DataTables CSS -->
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.css">
        <!-- jQuery -->
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <!-- DataTables JS -->
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.js"></script>
    </head>
    <body>
        {plot_div}
        {full_tables_html}
        {explanation_text}
        {timestamp_html}
        <script>
            $(document).ready(function() {{
                $('#top5_table').DataTable({{
                    "pageLength": 5,
                    "lengthMenu": [5, 10, 25, 50],
                    "paging": false,  // Deaktiviert die Paginierung für Top 5 und Bottom 5
                    "searching": false  // Deaktiviert die Suche für Top 5 und Bottom 5
                }});
                $('#bottom5_table').DataTable({{
                    "pageLength": 5,
                    "lengthMenu": [5, 10, 25, 50],
                    "paging": false,
                    "searching": false
                }});
                $('#full_table').DataTable({{
                    "pageLength": 10,
                    "lengthMenu": [5, 10, 25, 50],
                    "paging": true,
                    "searching": true
                }});
            }});
        </script>
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
        return HTMLResponse(content="COC_EMAIL oder COC_PASSWORD ist nicht gesetzt. Bitte überprüfen Sie Ihre Environment Variables.", status_code=500)

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

# Mangum Handler hinzufügen
handler = Mangum(app)
