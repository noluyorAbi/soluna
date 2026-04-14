import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import coc
import asyncio
import plotly.express as px
from fastapi import FastAPI, Response, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import html  # Für HTML-Escaping
from mangum import Mangum  # Importiere Mangum für die Integration mit Vercel
from io import StringIO

# Schriftart anpassen, um fehlende Glyphen zu vermeiden
plt.rcParams['font.family'] = 'DejaVu Sans'  # 'DejaVu Sans' ist standardmäßig in matplotlib enthalten

# dotenv laden (nur lokal nützlich, Vercel verwendet Environment Variables)
load_dotenv()

# Clash of Clans API E-Mail und Passwort aus Environment Variables laden
COC_EMAIL = os.getenv('COC_EMAIL')
COC_PASSWORD = os.getenv('COC_PASSWORD')
CLAN_TAG = '#2LUVL2QGL'  # Ersetzen Sie dies mit Ihrem Clan-Tag


"""  INITAL
DONATION_WEIGHT = 1.0           # Gewichtung für Spenden Gegeben
DONATION_RECEIVED_WEIGHT = 0.5  # Gewichtung für Spenden Erhalten
ATTACK_WIN_WEIGHT = 1.5         # Basisgewichtung für gewonnene Angriffe
TROPHY_SCALE = 1000.0           # Skalierungsfaktor für Trophäen
ATTACK_BASE_WEIGHT = 1.0        # Basisgewichtungsfaktor zusätzlich zum Skalierungsfaktor
 """

# Gewichtungsfaktoren einstellen (können nach Bedarf angepasst werden)
DONATION_WEIGHT = 0.3           # Geringere Gewichtung für Spenden
DONATION_RECEIVED_WEIGHT = 0.1  # Geringere Gewichtung für erhaltene Spenden
ATTACK_WIN_WEIGHT = 3.0         # Stärkere Gewichtung für gewonnene Angriffe
TROPHY_SCALE = 500.0           # Zweitrangige Gewichtung für Trophäen
ATTACK_BASE_WEIGHT = 1.0        # Basisgewicht für Angriffe


# FastAPI-App initialisieren
app = FastAPI()

origins = [
    "http://localhost:3000",  # Port Ihres Next.js-Entwicklungsservers
    "https://soluna-nine.vercel.app",  # Fügen Sie weitere Ursprünge hinzu, wenn nötig
    "https://soluna-production.up.railway.app",  # Produktionsfrontend
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

        role_obj = getattr(player, 'role', None)
        role_str = getattr(role_obj, 'in_game_name', None)
        if not role_str and role_obj is not None:
            role_str = str(role_obj).split('.')[-1]
        role_str = role_str or 'Mitglied'

        league_obj = getattr(player, 'league', None)
        league_str = getattr(league_obj, 'name', None) or 'Unranked'

        return {
            'name': player.name,
            'trophies': player.trophies or 0,
            'best_trophies': getattr(player, 'best_trophies', 0) or 0,
            'donations': player.donations or 0,
            'donationsReceived': player.received or 0,
            'attackWins': player.attack_wins or 0,
            'defenseWins': getattr(player, 'defense_wins', 0) or 0,
            'warStars': getattr(player, 'war_stars', 0) or 0,
            'townHall': getattr(player, 'town_hall', 0) or 0,
            'expLevel': getattr(player, 'exp_level', 0) or 0,
            'clanRank': getattr(player, 'clan_rank', 0) or 0,
            'role': role_str,
            'league': league_str,
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

def create_interactive_activity_plot(members_data, clan_tag=CLAN_TAG, donation_weight=1.0, donation_received_weight=0.5,
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

    # Sicherstellen, dass Kriegs-Sterne vorhanden sind (für v2-Score)
    if 'warStars' not in df.columns:
        df['warStars'] = 0

    # --- Aktivitäts-Score v3 — brutale, ungedeckelte Linearsumme ------------
    # Reale Rohwerte, keine Sättigung. Wer 10× leistet, hat 10× Punkte.
    # Trophäen-Bonus bounded [0,8; 1,3] für TH-Fairness (kein Score-Cap).
    #   1 Spende gegeben        = 1 Pkt
    #   1 Angriffssieg          = 3 · m_T Pkt   (m_T ∈ [0,8; 1,3])
    #   1 Kriegs-Stern (life.)  = 0,5 Pkt
    SCORE_ATT_WEIGHT = 3.0
    SCORE_WAR_WEIGHT = 0.5

    trophy_mult = 0.8 + 0.5 * (
        df['trophies'].astype(float) / 5000.0
    ).clip(lower=0.0, upper=1.0)

    df['score_don'] = df['donations'].astype(float).round(1)
    df['score_att'] = (SCORE_ATT_WEIGHT * df['attackWins'].astype(float) * trophy_mult).round(1)
    df['score_war'] = (SCORE_WAR_WEIGHT * df['warStars'].astype(float)).round(1)
    df['Aktivität'] = (df['score_don'] + df['score_att'] + df['score_war']).round(1)

    # Legacy v1 und v2 für Vergleichszwecke (nicht prominent angezeigt)
    df['Aktivität_v1'] = (
        (df['donations'] * donation_weight)
        + (df['donationsReceived'] * donation_received_weight)
        + (df['attackWins'] * (attack_base_weight + df['trophies'] / trophy_scale))
    ).round(2)

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

    # Sicherstellen, dass neue Spalten existieren (für ältere Ausführungspfade)
    for col, default in [
        ('best_trophies', 0), ('defenseWins', 0), ('warStars', 0),
        ('townHall', 0), ('expLevel', 0), ('clanRank', 0),
        ('role', 'Mitglied'), ('league', 'Unranked'),
    ]:
        if col not in df.columns:
            df[col] = default

    df['Netto_Spenden'] = df['donations'] - df['donationsReceived']

    mean_activity = df['Aktivität'].mean()
    median_activity = df['Aktivität'].median()
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

    top_5 = df.head(5)
    bottom_5 = df.tail(5)
    top_5_html = generate_html_table(top_5, "Top 5 Aktive Clan-Mitglieder", "top5_table")
    bottom_5_html = generate_html_table(bottom_5, "Bottom 5 Aktive Clan-Mitglieder", "bottom5_table")
    full_table_html = generate_full_html_table(df, "Alle Clan-Mitglieder", "full_table")

    import plotly.graph_objects as go

    # ---------- Palette (Light) ----------
    P = {
        'bg': '#f8fafc', 'surface': '#ffffff', 'subtle': '#f1f5f9',
        'border': '#e2e8f0', 'text': '#0f172a', 'muted': '#475569',
        'accent': '#2563eb', 'accent2': '#7c3aed',
        'ok': '#059669', 'warn': '#d97706', 'bad': '#dc2626',
        'teal': '#0891b2', 'pink': '#db2777', 'indigo': '#4f46e5',
    }
    qcolors = {
        'Unteres 25%': P['bad'], 'Mittleres 50%': P['warn'],
        'Oberes 25%': P['ok'], 'Sehr hoch': P['accent'],
    }
    layout_base = dict(
        template='plotly_white',
        paper_bgcolor=P['surface'], plot_bgcolor=P['surface'],
        font=dict(color=P['text'], family='Inter, system-ui, sans-serif', size=12),
        margin=dict(l=50, r=30, t=60, b=50),
        colorway=[P['accent'], P['ok'], P['warn'], P['pink'], P['indigo'], P['teal']],
        xaxis=dict(gridcolor='#eef2f7', zerolinecolor='#d0d7e2', linecolor='#cbd5e1'),
        yaxis=dict(gridcolor='#eef2f7', zerolinecolor='#d0d7e2', linecolor='#cbd5e1'),
        legend=dict(bgcolor='rgba(255,255,255,0.92)', bordercolor=P['border'], borderwidth=1),
        title_font=dict(size=16, color=P['text']),
        hoverlabel=dict(bgcolor='white', bordercolor=P['border'], font=dict(color=P['text'])),
    )

    # ---------- Icons (Lucide-style, inline SVG) ----------
    ICONS = {
        'users': '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.87"/>',
        'activity': '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        'up': '<circle cx="12" cy="12" r="10"/><polyline points="16 12 12 8 8 12"/><line x1="12" y1="16" x2="12" y2="8"/>',
        'down': '<circle cx="12" cy="12" r="10"/><polyline points="8 12 12 16 16 12"/><line x1="12" y1="8" x2="12" y2="16"/>',
        'scale': '<path d="M12 3v18"/><path d="M5 7l-3 9c1 2 5 2 6 0L5 7z"/><path d="M19 7l-3 9c1 2 5 2 6 0L19 7z"/><path d="M3 7h18"/>',
        'sword': '<path d="M14.5 17.5L3 6V3h3l11.5 11.5"/><path d="M13 19l6-6"/><path d="M16 16l4 4"/><path d="M19 21l2-2"/>',
        'trophy': '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>',
        'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        'home': '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
        'lightbulb': '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/>',
        'info': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
        'bar': '<line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/><line x1="3" y1="20" x2="21" y2="20"/>',
        'pie': '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>',
        'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        'alert': '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        'check': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
        'back': '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
        'book': '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        'gauge': '<path d="M12 14l4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
        'layers': '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
        'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        'zap': '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    }
    def ic(name, size=18, cls='ic'):
        return ('<svg class="' + cls + '" width="' + str(size) + '" height="' + str(size) +
                '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
                ICONS.get(name, '') + '</svg>')

    # ---------- 1. Activity scatter ----------
    fig = px.scatter(
        df, x='Spieler_ID', y='Aktivität',
        color='Quantil', color_discrete_map=qcolors,
        custom_data=['name', 'trophies', 'donations', 'donationsReceived',
                     'attackWins', 'Spenden_Verhältnis', 'Aktivität', 'townHall', 'role'],
        labels={'Spieler_ID': 'Rang', 'Aktivität': 'Aktivitäts-Score'},
        title='Aktivitäts-Score je Spieler (sortiert, Quartile farbkodiert)'
    )
    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color='#ffffff')),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>Rang %{x} · Aktivität %{customdata[6]:.2f}<br>'
            'Rathaus %{customdata[7]} · %{customdata[8]}<br>'
            'Trophäen %{customdata[1]} · Angriffe %{customdata[4]}<br>'
            'Spenden ↑%{customdata[2]} ↓%{customdata[3]} (Ratio %{customdata[5]})<extra></extra>'
        ),
    )
    fig.add_hline(y=mean_activity, line_dash='dash', line_color=P['accent'], opacity=0.75,
                  annotation_text='Ø ' + str(round(mean_activity, 1)),
                  annotation_position='top left', annotation_font_color=P['accent'])
    fig.add_hline(y=median_activity, line_dash='dot', line_color=P['ok'], opacity=0.75,
                  annotation_text='Median ' + str(round(median_activity, 1)),
                  annotation_position='bottom left', annotation_font_color=P['ok'])
    fig.update_layout(**layout_base, height=520)

    # ---------- 2. Donations grouped bar ----------
    df_don = df.sort_values('Netto_Spenden', ascending=True)
    don_fig = go.Figure()
    don_fig.add_bar(y=df_don['name'], x=df_don['donations'], name='Gegeben',
                    orientation='h', marker_color=P['ok'],
                    hovertemplate='<b>%{y}</b><br>Gegeben: %{x}<extra></extra>')
    don_fig.add_bar(y=df_don['name'], x=-df_don['donationsReceived'], name='Erhalten',
                    orientation='h', marker_color=P['pink'],
                    hovertemplate='<b>%{y}</b><br>Erhalten: %{customdata}<extra></extra>',
                    customdata=df_don['donationsReceived'])
    don_layout = {k: v for k, v in layout_base.items() if k not in ('xaxis', 'yaxis')}
    don_fig.update_layout(
        title_text='Spenden · Gegeben (rechts) vs. Erhalten (links)',
        barmode='overlay', bargap=0.15,
        xaxis=dict(title='Spenden', gridcolor='#eef2f7', zerolinecolor='#94a3b8'),
        yaxis=dict(title='', gridcolor='#ffffff'),
        height=max(420, 26 * len(df) + 120),
        **don_layout,
    )

    # ---------- 3. Histogram + box ----------
    hist_fig = px.histogram(df, x='Aktivität',
                            nbins=max(8, min(20, len(df) // 2 + 4)),
                            marginal='box', title='Verteilung des Aktivitäts-Scores',
                            color_discrete_sequence=[P['accent']])
    hist_fig.update_traces(marker_line_color='#ffffff', marker_line_width=1)
    hist_fig.update_layout(**layout_base, bargap=0.05, height=420)

    # ---------- 4. Attack vs. Trophy bubble ----------
    bubble = px.scatter(
        df, x='trophies', y='attackWins',
        size=df['donations'].clip(lower=1),
        color='townHall', color_continuous_scale='Plasma',
        custom_data=['name', 'donations', 'role', 'townHall'],
        title='Kampf-Profil · Angriffe vs. Trophäen (Größe = Spenden)',
        labels={'trophies': 'Trophäen', 'attackWins': 'Gewonnene Angriffe'},
    )
    bubble.update_traces(
        hovertemplate=('<b>%{customdata[0]}</b><br>TH %{customdata[3]} · %{customdata[2]}<br>'
                       'Trophäen %{x} · Angriffe %{y}<br>Spenden gegeben: %{customdata[1]}<extra></extra>'),
        marker=dict(line=dict(color='#ffffff', width=1)),
    )
    bubble.update_layout(**layout_base, height=440,
                         coloraxis_colorbar=dict(title='Rathaus'))

    # ---------- 5. TH donut ----------
    th_counts = df.groupby('townHall').size().reset_index(name='count').sort_values('townHall')
    th_fig = px.pie(th_counts, names='townHall', values='count', hole=0.58,
                    title='Rathaus-Verteilung',
                    color_discrete_sequence=px.colors.sequential.Blues[2:])
    th_fig.update_traces(textinfo='label+value',
                         marker=dict(line=dict(color='#ffffff', width=2)),
                         hovertemplate='Rathaus %{label}<br>%{value} Spieler (%{percent})<extra></extra>')
    th_fig.update_layout(**layout_base, height=420)

    # ---------- 6. Role donut ----------
    role_counts = df.groupby('role').size().reset_index(name='count')
    role_fig = px.pie(role_counts, names='role', values='count', hole=0.58,
                      title='Rollen-Verteilung',
                      color_discrete_sequence=[P['accent'], P['teal'], P['warn'], P['pink'], P['indigo']])
    role_fig.update_traces(textinfo='label+value',
                           marker=dict(line=dict(color='#ffffff', width=2)),
                           hovertemplate='<b>%{label}</b><br>%{value} Spieler (%{percent})<extra></extra>')
    role_fig.update_layout(**layout_base, height=420)

    # ---------- 7. Treemap ----------
    df_tree = df.copy()
    df_tree['donations_pos'] = df_tree['donations'].clip(lower=1)
    tree_fig = px.treemap(
        df_tree, path=['role', 'name'], values='donations_pos',
        color='Aktivität', color_continuous_scale='Viridis',
        title='Beitrags-Treemap · Fläche = Spenden gegeben · Farbe = Aktivität',
        custom_data=['donations', 'attackWins', 'trophies', 'Aktivität'],
    )
    tree_fig.update_traces(
        hovertemplate=('<b>%{label}</b><br>Spenden: %{customdata[0]}<br>'
                       'Angriffe: %{customdata[1]} · Trophäen: %{customdata[2]}<br>'
                       'Aktivität: %{customdata[3]:.2f}<extra></extra>'),
        marker=dict(line=dict(color='#ffffff', width=2)),
    )
    tree_fig.update_layout(**layout_base, height=480)

    def fig_div(f, with_js=False):
        return f.to_html(
            include_plotlyjs='cdn' if with_js else False,
            full_html=False,
            config={'displaylogo': False, 'responsive': True},
        )

    scatter_div = fig_div(fig, with_js=True)
    don_div = fig_div(don_fig)
    hist_div = fig_div(hist_fig)
    bubble_div = fig_div(bubble)
    th_div = fig_div(th_fig)
    role_div = fig_div(role_fig)
    tree_div = fig_div(tree_fig)

    # ---------- Metrics ----------
    n = len(df)
    total_don = int(df['donations'].sum())
    total_rec = int(df['donationsReceived'].sum())
    total_att = int(df['attackWins'].sum())
    total_troph = int(df['trophies'].sum())
    total_war = int(df['warStars'].sum())
    net_don = total_don - total_rec
    avg_don = total_don / n if n else 0
    avg_att = total_att / n if n else 0
    avg_troph = total_troph / n if n else 0
    avg_war = total_war / n if n else 0
    avg_act = mean_activity

    th_vals = df['townHall'].replace(0, pd.NA).dropna()
    th_avg = float(th_vals.mean()) if not th_vals.empty else 0
    th_min = int(th_vals.min()) if not th_vals.empty else 0
    th_max = int(th_vals.max()) if not th_vals.empty else 0

    above_avg = int((df['Aktivität'] > mean_activity).sum())
    inactive_mask = (df['donations'] < 50) & (df['attackWins'] < 20)
    inactive_count = int(inactive_mask.sum())
    inactive_names = df[inactive_mask]['name'].tolist()

    top_donor = df.loc[df['donations'].idxmax()]
    top_attacker = df.loc[df['attackWins'].idxmax()]
    top_trophy = df.loc[df['trophies'].idxmax()]
    top_warstar = df.loc[df['warStars'].idxmax()]

    top10_n = max(1, n // 10)
    top10_share = (df.nlargest(top10_n, 'donations')['donations'].sum() / total_don * 100) if total_don else 0

    global_ratio = total_don / total_rec if total_rec else (float('inf') if total_don else 0)
    if global_ratio == 0:
        global_ratio_str = '—'
    elif global_ratio == float('inf'):
        global_ratio_str = '∞'
    else:
        global_ratio_str = f'{global_ratio:.2f}'

    # Status helpers
    def s_act(v): return 'bad' if v < 100 else 'warn' if v < 500 else 'ok' if v < 1500 else 'excellent'
    def s_don(v): return 'bad' if v < 100 else 'warn' if v < 500 else 'ok' if v < 1500 else 'excellent'
    def s_att(v): return 'bad' if v < 20 else 'warn' if v < 100 else 'ok' if v < 300 else 'excellent'
    def s_trp(v): return 'bad' if v < 1500 else 'warn' if v < 2500 else 'ok' if v < 4000 else 'excellent'
    def s_war(v): return 'bad' if v < 200 else 'warn' if v < 800 else 'ok' if v < 2000 else 'excellent'
    def s_net(v): return 'ok' if v > 0 else ('warn' if v == 0 else 'bad')
    def s_ratio(v):
        if v == 0: return 'bad'
        if v == float('inf') or v >= 2: return 'excellent'
        if v >= 1: return 'ok'
        if v >= 0.5: return 'warn'
        return 'bad'
    status_label = {'bad': 'schwach', 'warn': 'solide', 'ok': 'stark', 'excellent': 'exzellent'}

    cards_data = [
        ('users', 'Clan-Größe', f'{n}', 'von max. 50', 'ok'),
        ('zap', 'Aktive Mitglieder', f'{above_avg} / {n}',
         f'{(above_avg/n*100 if n else 0):.0f}% über Ø', 'ok' if above_avg >= n / 2 else 'warn'),
        ('activity', 'Ø Aktivität', f'{avg_act:.1f}',
         f'Median {median_activity:.0f}', s_act(avg_act)),
        ('scale', 'Netto-Spenden', f'{net_don:+,}', 'Gegeben − Erhalten', s_net(net_don)),
        ('up', 'Spenden gegeben', f'{total_don:,}',
         f'Ø {avg_don:.0f}/Spieler', s_don(avg_don)),
        ('down', 'Spenden-Verhältnis', global_ratio_str,
         'Global gegeben/erhalten', s_ratio(global_ratio)),
        ('sword', 'Angriffe gewonnen', f'{total_att:,}',
         f'Ø {avg_att:.0f}/Spieler', s_att(avg_att)),
        ('trophy', 'Trophäen Ø', f'{avg_troph:.0f}',
         f'Top: {int(top_trophy["trophies"]):,}', s_trp(avg_troph)),
        ('star', 'Kriegs-Sterne', f'{total_war:,}',
         f'Ø {avg_war:.0f}/Spieler', s_war(avg_war)),
        ('home', 'Rathaus-Niveau', f'TH{th_avg:.1f}',
         f'Spanne TH{th_min}–TH{th_max}', 'ok'),
    ]
    cards_html = '<div class="cards">' + ''.join(
        '<div class="card status-' + status + '">'
        + '<div class="card-top">' + ic(icn, 18, 'ic ic-card')
        + '<span class="card-label">' + label + '</span>'
        + '<span class="card-chip">' + status_label[status] + '</span></div>'
        + '<div class="card-value">' + str(val) + '</div>'
        + '<div class="card-sub">' + str(sub) + '</div>'
        + '</div>'
        for (icn, label, val, sub, status) in cards_data
    ) + '</div>'

    # ---------- Auto-Interpretation ----------
    def pct(val, total):
        return (val / total * 100) if total else 0

    pct_above = pct(above_avg, n)

    # Skew detection with plain-language explanation
    if mean_activity > median_activity * 1.15:
        skew_label = 'rechts-schief (linksgipflig)'
        skew_meta = (
            '<b>Was heißt rechts-schief?</b> Einige wenige sehr aktive Mitglieder ziehen '
            'den <b>Durchschnitt</b> (' + f'{avg_act:.1f}' + ') über das Mittelfeld '
            '(<b>Median</b> ' + f'{median_activity:.1f}' + ') hinaus. In so einer Verteilung '
            'zeigt der Median den „typischen" Spieler zuverlässiger als der Durchschnitt. '
            'Man erkennt das auch im Scatter unten: ein paar Punkte hoch oben, der Rest '
            'liegt deutlich tiefer.'
        )
    elif mean_activity < median_activity * 0.9:
        skew_label = 'links-schief (rechtsgipflig)'
        skew_meta = (
            '<b>Was heißt links-schief?</b> Die meisten Mitglieder liegen relativ weit oben, '
            'aber einzelne sehr inaktive Spieler ziehen den <b>Durchschnitt</b> (' + f'{avg_act:.1f}'
            + ') unter das Mittelfeld (<b>Median</b> ' + f'{median_activity:.1f}' + '). '
            'Die Spitze ist breit, die Schwachstellen sind Einzelfälle.'
        )
    else:
        skew_label = 'ausgewogen (symmetrisch)'
        skew_meta = (
            '<b>Ausgewogen</b> bedeutet: Durchschnitt und Median liegen dicht beieinander — '
            'keine extremen Ausreißer in eine Richtung. Beide Kennzahlen sind hier gleich '
            'aussagekräftig.'
        )

    insights = []

    insights.append({
        'kind': 'activity',
        'title': 'Aktivitäts-Profil',
        'body': (
            'Der Clan erreicht im <b>Durchschnitt</b> ' + f'{avg_act:.1f}' + ' Punkte, im '
            '<b>Median</b> ' + f'{median_activity:.1f}' + ' Punkte. '
            '<b>' + str(above_avg) + ' von ' + str(n) + '</b> Spielern '
            '(<b>' + f'{pct_above:.0f}' + '%</b>) liegen über dem Durchschnitt. '
            'Die Verteilung ist <b>' + skew_label + '</b>.'
        ),
        'meta': skew_meta,
    })

    # Donation balance with plain explanation
    if net_don > 0:
        don_meta = (
            '<b>Netto-Spenden</b> = gegeben minus erhalten. Ein <b>positiver</b> Wert heißt: '
            'der Clan liefert mehr, als er verbraucht — <b>gesund</b>. Mitglieder '
            'unterstützen sich gegenseitig, niemand zehrt systematisch an den anderen.'
        )
    elif net_don < 0:
        don_meta = (
            '<b>Netto-Spenden</b> = gegeben minus erhalten. Der <b>negative</b> Wert bedeutet: '
            'insgesamt wird mehr angefordert als geliefert. Einzelne Top-Geber können das '
            'zeitweise ausgleichen — auf Dauer aber ein Warnzeichen, oft Zeichen '
            'schwindender Aktivität.'
        )
    else:
        don_meta = (
            '<b>Netto-Spenden</b> = gegeben minus erhalten. Hier ausgeglichen: '
            'Angebot und Nachfrage decken sich.'
        )
    insights.append({
        'kind': 'donations',
        'title': 'Spenden-Bilanz',
        'body': (
            '<b>Gegeben:</b> ' + f'{total_don:,}' + ' · <b>Erhalten:</b> '
            + f'{total_rec:,}' + ' · <b>Netto:</b> ' + f'{net_don:+,}' + '.'
        ),
        'meta': don_meta,
    })

    # Top donor
    top_share = pct(top_donor['donations'], total_don)
    if top_share > 25:
        top_meta = (
            'Ein einzelner Spieler liefert über <b>25%</b> aller Clan-Spenden — das ist '
            '<b>tragend, aber risikobehaftet</b>. Verlässt dieser Spieler den Clan, bricht '
            'die Versorgung spürbar ein.'
        )
    elif top_share > 15:
        top_meta = (
            'Ein Anteil von <b>15–25%</b> ist überdurchschnittlich, aber noch im normalen '
            'Bereich. Ein zweiter starker Spender würde den Clan robuster machen.'
        )
    else:
        top_meta = (
            'Anteil unter <b>15%</b> — gesunde Breite. Der Clan hängt nicht an einer '
            'einzelnen Person.'
        )
    insights.append({
        'kind': 'top-donor',
        'title': 'Top-Spender',
        'body': (
            '<b>' + html.escape(str(top_donor['name'])) + '</b> mit '
            '<b>' + f'{int(top_donor["donations"]):,}' + '</b> Spenden — das sind '
            '<b>' + f'{top_share:.1f}%</b> aller Clan-Spenden.'
        ),
        'meta': top_meta,
    })

    # Concentration
    if top10_share > 60:
        conc_meta = (
            'Über <b>60%</b> aller Spenden kommen von 10% der Mitglieder — der Clan ist '
            '<b>stark abhängig</b> von wenigen Leistungsträgern. Wandern die ab, bricht die '
            'Versorgung ein.'
        )
    elif top10_share > 40:
        conc_meta = (
            '<b>40–60%</b> gilt als <b>konzentriert, aber tragbar</b>. Ein breiterer '
            'Mittelbau an Gebern würde den Clan stabiler machen.'
        )
    else:
        conc_meta = (
            'Unter <b>40%</b> Konzentration ist <b>gesund</b> — Spenden kommen aus einer '
            'breiten Mitte, nicht nur aus ein paar Händen. (Konzentration = Anteil der '
            'obersten 10% am Gesamthandel.)'
        )
    insights.append({
        'kind': 'inequality',
        'title': 'Konzentration der Spitze',
        'body': (
            'Die stärksten <b>10%</b> (' + str(top10_n) + ' Spieler) liefern '
            '<b>' + f'{top10_share:.0f}' + '%</b> aller Spenden.'
        ),
        'meta': conc_meta,
    })

    # Attacks — adjust meta to current phase
    if avg_att < 5:
        att_meta = (
            'Angriffe werden zu <b>jedem Saisonwechsel auf 0 zurückgesetzt</b>. Niedrige '
            'Zahlen bedeuten hier meistens: <b>die Saison ist gerade erst gestartet</b>. '
            'Aussagekraft nimmt gegen Saisonende deutlich zu.'
        )
    elif avg_att < 50:
        att_meta = (
            'Moderate Kampfaktivität. Angriffe werden zu Saisonbeginn zurückgesetzt — '
            'wenn das Saisonende näher rückt, sollte dieser Wert deutlich steigen.'
        )
    else:
        att_meta = (
            'Hohe Kampfaktivität im Clan. Achtung: Angriffe sind Saisonwerte (werden bei '
            'Saisonwechsel zurückgesetzt), die Zahl zeigt also nicht die Lebensleistung, '
            'sondern nur die aktuelle Phase.'
        )
    insights.append({
        'kind': 'attacks',
        'title': 'Kampfaktivität (aktuelle Saison)',
        'body': (
            '<b>' + f'{total_att:,}' + '</b> gewonnene Angriffe gesamt, Ø <b>'
            + f'{avg_att:.0f}' + '</b> pro Spieler. Top-Angreifer: <b>'
            + html.escape(str(top_attacker['name']))
            + '</b> (' + str(int(top_attacker['attackWins'])) + ' Siege).'
        ),
        'meta': att_meta,
    })

    # Trophies
    trophy_meta = (
        'Trophäen zeigen das <b>aktuelle Angriffsniveau</b> (je höher die Trophäen, desto '
        'stärker die Gegner). Grobe Orientierung: <b>&lt; 1.500</b> Einsteiger, '
        '<b>1.500–3.000</b> Mittelfeld, <b>3.000–5.000</b> erfahren, '
        '<b>5.000+</b> Legende-Liga. Trophäen fallen durch Verteidigungen und steigen durch '
        'eigene Siege.'
    )
    insights.append({
        'kind': 'trophies',
        'title': 'Trophäen-Niveau',
        'body': (
            '<b>' + html.escape(str(top_trophy['name'])) + '</b> führt mit <b>'
            + f'{int(top_trophy["trophies"]):,}' + '</b> Trophäen. '
            'Clan-Durchschnitt: <b>' + f'{avg_troph:.0f}' + '</b>.'
        ),
        'meta': trophy_meta,
    })

    # War
    insights.append({
        'kind': 'war',
        'title': 'Kriegs-Erfahrung',
        'body': (
            '<b>' + f'{total_war:,}' + '</b> Kriegs-Sterne insgesamt, Ø <b>'
            + f'{avg_war:.0f}' + '</b> pro Spieler. Erfahrendster Krieger: <b>'
            + html.escape(str(top_warstar['name'])) + '</b> ('
            + f'{int(top_warstar["warStars"]):,}' + ' Sterne).'
        ),
        'meta': (
            'Kriegs-Sterne sind <b>lebenslang kumulativ</b> — sie zeigen langjähriges '
            'Kriegsengagement, nicht die aktuelle Saison. Hohe Einzelwerte = erfahrene '
            'Clan-Kriegsveteranen. Ø über 500 gilt bereits als ambitionierter Kriegsclan.'
        ),
    })

    # Composition
    role_breakdown = ', '.join(
        str(cnt) + '× ' + html.escape(str(role_n))
        for role_n, cnt in df['role'].value_counts().items()
    )
    if th_max - th_min >= 6:
        comp_meta = (
            'Große <b>TH-Spanne</b> (TH' + str(th_min) + '–TH' + str(th_max) + '): '
            'vielfältiger Clan, aber beim <b>Clan-Krieg-Matchmaking</b> schwieriger — '
            'der Gegner-Clan könnte viel höhere TH-Levels haben als einige eurer Spieler, '
            'die dann keine realistischen Gegner finden.'
        )
    elif th_max - th_min >= 3:
        comp_meta = (
            'Mittlere TH-Spanne — typisch für gewachsene Clans. Im Krieg gut händelbar, '
            'solange niedrige TH-Level nicht gegen viel stärkere Gegner antreten müssen.'
        )
    else:
        comp_meta = (
            'Enge TH-Spanne — sehr homogener Clan. Ideal für <b>ausgeglichene '
            'Kriegspaarungen</b> (Matchmaking findet gleichwertige Gegner). '
            'Nachteil: weniger Raum für neue/aufsteigende Spieler.'
        )
    insights.append({
        'kind': 'composition',
        'title': 'Clan-Zusammensetzung',
        'body': (
            'Rathäuser: <b>TH' + str(th_min) + '–TH' + str(th_max) + '</b> (Ø TH'
            + f'{th_avg:.1f}' + '). Rollen: ' + role_breakdown + '.'
        ),
        'meta': comp_meta,
    })

    # Inactive
    if inactive_count:
        preview = ', '.join(html.escape(str(x)) for x in inactive_names[:5])
        if len(inactive_names) > 5:
            preview += '…'
        insights.append({
            'kind': 'alert',
            'title': 'Potenziell inaktive Mitglieder (' + str(inactive_count) + ')',
            'body': preview,
            'meta': (
                '<b>Wie erkannt?</b> Weniger als <b>50 gegebene Spenden</b> UND weniger '
                'als <b>20 gewonnene Angriffe</b> in der aktuellen Saison. Das kann auf '
                'Pause, Urlaub oder Abwanderung hindeuten. Einzelfallweise ansprechen '
                'statt direkt kicken — manchmal sind es Neueinsteiger, die gerade erst '
                'dazugestoßen sind.'
            ),
        })
    else:
        insights.append({
            'kind': 'check',
            'title': 'Gute Aktivitätslage',
            'body': 'Kein Mitglied fällt mit sehr niedrigen Spenden UND Angriffen auf.',
            'meta': (
                '<b>Kriterium:</b> mindestens 50 Spenden oder 20 Angriffe pro Spieler. '
                'Alle Mitglieder sind also aktiv im Clan-Betrieb.'
            ),
        })

    kind_icon = {
        'activity': 'activity', 'donations': 'scale', 'top-donor': 'star',
        'inequality': 'pie', 'attacks': 'sword', 'trophies': 'trophy',
        'war': 'shield', 'composition': 'layers',
        'alert': 'alert', 'check': 'check',
    }
    insights_html = ''.join(
        '<div class="insight insight-' + d['kind'] + '">'
        + ic(kind_icon.get(d['kind'], 'info'), 20)
        + '<div>'
        + '<div class="insight-title">' + d['title'] + '</div>'
        + '<div class="insight-body">' + d['body'] + '</div>'
        + '<div class="insight-meta">' + d['meta'] + '</div>'
        + '</div></div>'
        for d in insights
    )
    interp_panel = (
        '<div class="explain-block">'
        '<div class="section-head">' + ic('lightbulb', 22)
        + '<span>Automatische Interpretation</span></div>'
        '<p class="explain-hint">Jede Kachel zeigt oben einen <b>Fakt</b> aus den Daten — '
        'darunter steht in einfacher Sprache, <b>was das bedeutet</b>. Fachbegriffe '
        '(Median, Konzentration, Schiefe, Saisonwerte &hellip;) werden jeweils kurz erklärt.</p>'
        '<div class="insights">' + insights_html + '</div>'
        '</div>'
    )

    # ---------- Reference guide ----------
    ref_rows = [
        ('Spenden gegeben (Ø pro Spieler, Saison)', '&lt; 100', '100–500', '500–1.500', '&gt; 1.500'),
        ('Angriffe gewonnen (Ø pro Spieler, Saison)', '&lt; 20', '20–100', '100–300', '&gt; 300'),
        ('Trophäen (Ø pro Spieler)', '&lt; 1.500', '1.500–2.500', '2.500–4.000', '&gt; 4.000'),
        ('Kriegs-Sterne (Ø pro Spieler, gesamt)', '&lt; 200', '200–800', '800–2.000', '&gt; 2.000'),
        ('Spenden-Verhältnis (geben/erhalten)', '&lt; 0.5', '0.5–1.0', '1.0–2.0', '&gt; 2.0'),
        ('Aktivitäts-Score v3 (ungedeckelt, Saison)', '&lt; 100', '100–500', '500–1.500', '&gt; 1.500'),
    ]
    ref_table = (
        '<table class="ref-table"><thead><tr>'
        '<th>Metrik</th><th class="s-bad">schwach</th><th class="s-warn">solide</th>'
        '<th class="s-ok">stark</th><th class="s-exc">exzellent</th></tr></thead><tbody>'
        + ''.join('<tr><td>' + r[0] + '</td><td>' + r[1] + '</td><td>' + r[2]
                  + '</td><td>' + r[3] + '</td><td>' + r[4] + '</td></tr>' for r in ref_rows)
        + '</tbody></table>'
    )

    # ---------- Deep Explanation ----------
    explain_deep = (
        '<div class="explain-block">'
        '<div class="section-head">' + ic('gauge', 22) + '<span>Aktivitäts-Score v3 — brutale Wahrheit, ohne Cap</span></div>'
        '<p>Keine Sättigung, keine künstliche Obergrenze. Der Score ist eine <b>lineare '
        'Summe</b> von drei Rohwerten — wer 10× mehr leistet, hat 10× mehr Punkte. '
        'So bleibt die reale Aktivitätsspanne sichtbar, statt in einer 0–100-Skala '
        'plattgedrückt zu werden.</p>'

        '<h4>Gesamt-Formel</h4>'
        '<div class="formula">'
        r'$$\text{Score} = \underbrace{D_{\text{geg}}}_{\text{Spenden}} \;+\; '
        r'\underbrace{3 \cdot A \cdot m_T}_{\text{Angriffe}} \;+\; '
        r'\underbrace{0{,}5 \cdot W}_{\text{Kriegs-Sterne}}$$'
        '</div>'
        '<p><b>Legende:</b> '
        r'$D_{\text{geg}}$ Spenden gegeben (Saison) · '
        r'$A$ gewonnene Angriffe (Saison) · '
        r'$W$ Kriegs-Sterne (lifetime) · '
        r'$m_T$ Trophäen-Bonus.</p>'

        '<div class="ref-scroll"><table class="ref-table"><thead><tr>'
        '<th>Komponente</th><th>Pro Einheit</th><th>Anmerkung</th></tr></thead><tbody>'
        '<tr><td>Spenden gegeben</td><td>1 Pkt</td><td>linear, ungedeckelt</td></tr>'
        r'<tr><td>Angriffssieg</td><td>$3 \cdot m_T$ Pkt</td><td>Bonus $0{,}8 \le m_T \le 1{,}3$</td></tr>'
        '<tr><td>Kriegs-Stern (lifetime)</td><td>0,5 Pkt</td><td>halbiert, weil kumulativ</td></tr>'
        '</tbody></table></div>'

        '<h4>1 · Spenden-Anteil <span class="pill">linear</span></h4>'
        '<div class="formula">'
        r'$$\text{Spenden-Pkt} = \text{Spenden gegeben}$$'
        '</div>'
        '<p>Jede einzelne Spende = 1 Punkt. Transparent, nicht normiert. Wer 3000 Spenden '
        'liefert, sieht das direkt am Score.</p>'

        '<h4>2 · Angriffs-Anteil <span class="pill">trophäen-skaliert</span></h4>'
        '<div class="formula">'
        r'$$\text{Angriffs-Pkt} = 3 \cdot \text{Angriffe} \cdot m_T$$'
        '</div>'
        '<div class="formula">'
        r'$$m_T = 0{,}8 + 0{,}5 \cdot \min\!\left(1,\; \tfrac{\text{Trophäen}}{5000}\right) \;\in [0{,}8;\; 1{,}3]$$'
        '</div>'
        '<p>Ein Angriffssieg ist aufwändiger als eine Spende → <b>3×</b> gewichtet. Der '
        '<b>Trophäen-Bonus</b> $m_T$ liegt zwischen <b>0,8</b> (niedrige Ligen, einfache '
        'Gegner) und <b>1,3</b> (Legende, ab 5000 Trophäen). Faire TH-Gewichtung, '
        'aber keine Score-Deckelung.</p>'

        '<h4>3 · Kriegs-Anteil <span class="pill">lifetime</span></h4>'
        '<div class="formula">'
        r'$$\text{Kriegs-Pkt} = 0{,}5 \cdot \text{Kriegs-Sterne}$$'
        '</div>'
        '<p>Kriegs-Sterne sind <b>kumulativ</b> über die Spielerkarriere, daher <b>halb</b> '
        'gewichtet — sie gehören nicht zur aktuellen Saison. Ein Kriegsveteran erkennt '
        'man trotzdem deutlich am Score.</p>'

        '<h4>Rechenbeispiele</h4>'
        '<div class="ref-scroll"><table class="ref-table"><thead><tr>'
        '<th>Profil</th><th>Spenden</th><th>Angriffe (× Bonus)</th>'
        '<th>Sterne</th><th>Rechnung</th><th>Score</th></tr></thead><tbody>'
        '<tr><td>Aktiver TH13 (5000 Troph.)</td><td>800</td><td>150 × 1,3</td>'
        '<td>1.200</td><td>800 + 585 + 600</td><td><b>1.985</b></td></tr>'
        '<tr><td>Casual TH10 (2000 Troph.)</td><td>100</td><td>30 × 1,0</td>'
        '<td>200</td><td>100 + 90 + 100</td><td><b>290</b></td></tr>'
        '<tr><td>Leech TH14 (3000 Troph.)</td><td>20</td><td>5 × 1,1</td>'
        '<td>50</td><td>20 + 16,5 + 25</td><td><b>62</b></td></tr>'
        '</tbody></table></div>'

        '<h4>Was ist ein guter Score?</h4>'
        '<p>Orientierung (pro CoC-Saison, ca. 4 Wochen):</p>'
        '<ul>'
        '<li><span class="badge b-bad">&lt; 100</span> — kaum aktiv oder sehr neu im Clan.</li>'
        '<li><span class="badge b-warn">100–500</span> — solider Durchschnittsspieler.</li>'
        '<li><span class="badge b-ok">500–1.500</span> — sehr aktiv, wichtiges Clan-Mitglied.</li>'
        '<li><span class="badge b-exc">&gt; 1.500</span> — Leistungsträger, trägt den Clan maßgeblich.</li>'
        '</ul>'

        '<h4>Warum v3 statt v2?</h4>'
        '<ul>'
        '<li>v2 deckelte bei 100 Punkten — ein Whale mit 10.000 Spenden sah aus wie '
        'einer mit 2.000. Leistungsunterschiede wurden versteckt.</li>'
        '<li>v3 zeigt echte Größenordnungen. Ränge spiegeln wider, was tatsächlich '
        'geleistet wurde.</li>'
        '<li>Trophäen-Bonus bleibt beschränkt (0,8–1,3) für TH-Fairness — aber nichts '
        'sonst wird gecappt.</li>'
        '</ul>'

        '<h4>Alte Formeln <span class="pill">nur Vergleich</span></h4>'
        '<p><b>v1</b> (ursprünglich, Trophäen-Bonus unbeschränkt):</p>'
        '<div class="formula">'
        r'$$\text{Aktivität}_{v1} = 0{,}3 \cdot D_{\text{geg}} + 0{,}1 \cdot D_{\text{erh}} + A \cdot \left(1 + \tfrac{T}{500}\right)$$'
        '</div>'
        '<p><b>v2</b> (sättigend, 0–100 gedeckelt):</p>'
        '<div class="formula">'
        r'$$\text{Score}_{v2} = 100 \cdot \big[ 0{,}4\,\hat{D}_{\text{geg}} + 0{,}3\,\hat{A}\,m_T + 0{,}15\,\hat{W} + 0{,}15\,\text{Bal} \big]$$'
        '</div>'

        '<div class="note"><b>Hinweis:</b> Saisonwerte (Spenden, Angriffe) werden bei jedem '
        'Saisonwechsel auf 0 zurückgesetzt; Kriegs-Sterne bleiben kumulativ. Der Score ist '
        'damit eine <em>Saison-zentrierte Momentaufnahme</em> und gegen Saisonende am '
        'aussagekräftigsten.</div>'
        '</div>'

        '<div class="explain-block">'
        '<div class="section-head">' + ic('book', 22) + '<span>Orientierungswerte</span></div>'
        '<p>Richtwerte für typische Clans im Mittelfeld. Sehr junge oder sehr alte Clans liegen abweichend.</p>'
        '<div class="ref-scroll">' + ref_table + '</div>'
        '</div>'

        '<div class="explain-block">'
        '<div class="section-head">' + ic('pie', 22) + '<span>Spenden-Verhältnis</span></div>'
        '<p>Das Verhältnis <b>gegeben / erhalten</b> zeigt die Rolle eines Spielers im Clan-Handel:</p>'
        '<ul>'
        '<li><b>&gt; 2.0</b> — klarer Netto-Spender, trägt überdurchschnittlich zum Clan bei.</li>'
        '<li><b>1.0 – 2.0</b> — aktiver, ausgeglichener Spieler.</li>'
        '<li><b>0.5 – 1.0</b> — profitiert mehr als beiträgt, oft neue oder niedrige TH-Spieler.</li>'
        '<li><b>&lt; 0.5</b> — stark auf Empfangen ausgelegt; dauerhaft kritisch zu hinterfragen.</li>'
        '</ul>'
        '</div>'

        '<div class="explain-block">'
        '<div class="section-head">' + ic('target', 22) + '<span>Quartil-Farben im Aktivitäts-Scatter</span></div>'
        '<p>Jeder Spieler wird nach seinem Quartil eingefärbt: '
        '<span class="badge b-bad">Unteres 25%</span>'
        '<span class="badge b-warn">Mittleres 50%</span>'
        '<span class="badge b-ok">Oberes 25%</span>'
        '<span class="badge b-exc">Sehr hoch</span></p>'
        '<p>Die <b>gestrichelte Linie</b> markiert den Durchschnitt, die '
        '<b>gepunktete Linie</b> den Median. Ist der Abstand zwischen beiden groß, hat der Clan '
        'einige sehr starke Mitglieder, die den Schnitt verzerren — der Median ist dann '
        'aussagekräftiger als der Durchschnitt.</p>'
        '</div>'
    )

    current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    safe_tag = html.escape(clan_tag)

    css = (
        "*{box-sizing:border-box}"
        "html,body{margin:0;padding:0}"
        "body{background:#f8fafc;color:#0f172a;font-family:'Inter',system-ui,-apple-system,sans-serif;padding:28px 24px 40px;min-height:100vh}"
        "a{color:#2563eb;text-decoration:none}"
        ".header{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:16px;padding:0 4px 20px;border-bottom:1px solid #e2e8f0;margin-bottom:24px}"
        ".brand{display:flex;align-items:center;gap:14px}"
        ".brand-icon{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#2563eb,#7c3aed);display:flex;align-items:center;justify-content:center;color:white;box-shadow:0 10px 25px -12px rgba(37,99,235,0.55)}"
        ".title{font-size:26px;font-weight:700;letter-spacing:-0.4px;margin:0;color:#0f172a}"
        ".subtitle{color:#475569;font-size:13px;margin-top:4px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}"
        ".chip{background:#eff6ff;border:1px solid #bfdbfe;color:#1d4ed8;padding:3px 10px;border-radius:999px;font-size:12px;font-family:ui-monospace,monospace;font-weight:600}"
        ".meta{color:#64748b;font-size:12px}"
        ".actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}"
        ".btn{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:10px;font-weight:600;font-size:14px;text-decoration:none;border:1px solid transparent;cursor:pointer;transition:transform .15s ease, box-shadow .15s ease}"
        ".btn:hover{transform:translateY(-1px)}"
        ".btn-primary{background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;box-shadow:0 8px 20px -8px rgba(37,99,235,0.55)}"
        ".btn-secondary{background:#ffffff;color:#334155;border-color:#e2e8f0}"
        ".btn-secondary:hover{background:#f8fafc}"
        ".btn-success{background:linear-gradient(135deg,#059669,#10b981);color:white;box-shadow:0 8px 20px -8px rgba(16,185,129,0.55)}"
        ".btn[disabled]{opacity:.55;cursor:not-allowed;transform:none}"
        ".cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-bottom:26px}"
        ".card{background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:14px 16px;position:relative;overflow:hidden;box-shadow:0 1px 2px rgba(15,23,42,0.04)}"
        ".card::before{content:'';position:absolute;inset:0 auto auto 0;height:3px;width:100%;background:#e2e8f0}"
        ".card.status-bad::before{background:#dc2626}"
        ".card.status-warn::before{background:#d97706}"
        ".card.status-ok::before{background:#059669}"
        ".card.status-excellent::before{background:linear-gradient(90deg,#2563eb,#7c3aed)}"
        ".card-top{display:flex;align-items:center;gap:8px;color:#475569}"
        ".card-label{font-size:11px;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;color:#475569;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
        ".card-chip{font-size:10px;padding:2px 6px;border-radius:999px;background:#f1f5f9;color:#475569;text-transform:uppercase;letter-spacing:.04em;font-weight:700}"
        ".card.status-bad .card-chip{background:#fef2f2;color:#b91c1c}"
        ".card.status-warn .card-chip{background:#fffbeb;color:#b45309}"
        ".card.status-ok .card-chip{background:#ecfdf5;color:#047857}"
        ".card.status-excellent .card-chip{background:#eff6ff;color:#1d4ed8}"
        ".card-value{font-size:28px;font-weight:700;margin-top:6px;color:#0f172a;font-variant-numeric:tabular-nums;letter-spacing:-0.5px}"
        ".card-sub{color:#64748b;font-size:12px;margin-top:2px}"
        ".section-title{font-size:12px;font-weight:700;margin:32px 4px 14px;color:#475569;text-transform:uppercase;letter-spacing:0.14em;display:flex;gap:8px;align-items:center}"
        ".section-head{display:flex;align-items:center;gap:10px;font-weight:700;font-size:16px;color:#0f172a;margin-bottom:12px}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:18px}"
        ".panel{background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:12px;box-shadow:0 1px 3px rgba(15,23,42,0.04)}"
        ".panel.full{grid-column:1 / -1}"
        ".insights{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:10px;margin-top:6px}"
        ".insight{display:flex;gap:10px;align-items:flex-start;padding:12px 14px;border:1px solid #e2e8f0;border-radius:10px;background:#ffffff;color:#1e293b;font-size:13.5px;line-height:1.55}"
        ".insight > div:last-child{flex:1;min-width:0}"
        ".insight svg{flex:0 0 auto;margin-top:2px;color:#475569}"
        ".insight-title{font-weight:700;color:#0f172a;font-size:13.5px;margin-bottom:4px;letter-spacing:-0.1px}"
        ".insight-body{font-size:13.5px;line-height:1.55;color:#1e293b}"
        ".insight-body b{color:#0f172a}"
        ".insight-meta{margin-top:8px;padding-top:8px;border-top:1px dashed #e2e8f0;font-size:12.5px;color:#475569;line-height:1.55}"
        ".insight-meta b{color:#334155}"
        ".insight-alert .insight-meta{border-top-color:#fecaca;color:#7f1d1d}"
        ".insight-check .insight-meta{border-top-color:#a7f3d0;color:#065f46}"
        ".explain-hint{color:#64748b;font-size:13px;margin:-2px 0 14px;line-height:1.55}"
        ".glossary{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}"
        ".glossary .badge{cursor:help}"
        ".insight-alert{background:#fef2f2;border-color:#fecaca;color:#991b1b}"
        ".insight-alert svg{color:#dc2626}"
        ".insight-check{background:#ecfdf5;border-color:#a7f3d0;color:#065f46}"
        ".insight-check svg{color:#059669}"
        ".insight-activity svg{color:#2563eb}"
        ".insight-donations svg{color:#059669}"
        ".insight-top-donor svg{color:#d97706}"
        ".insight-inequality svg{color:#7c3aed}"
        ".insight-attacks svg{color:#db2777}"
        ".insight-trophies svg{color:#d97706}"
        ".insight-war svg{color:#0891b2}"
        ".insight-composition svg{color:#4f46e5}"
        ".explain-block{background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:18px 22px;margin-top:14px;box-shadow:0 1px 3px rgba(15,23,42,0.04)}"
        ".explain-block p,.explain-block li{color:#334155;line-height:1.65;font-size:14px}"
        ".explain-block h3,.explain-block h4{color:#0f172a}"
        ".formula{background:#f8fafc;border:1px dashed #cbd5e1;padding:12px 14px;border-radius:10px;font-family:ui-monospace,monospace;font-size:13px;color:#1e293b;margin:10px 0}"
        ".note{background:#fffbeb;border-left:4px solid #d97706;padding:10px 14px;border-radius:6px;color:#713f12;margin-top:10px;font-size:13px}"
        "table.ref-table{border-collapse:collapse;width:100%;margin-top:10px;font-size:13px}"
        "table.ref-table th,table.ref-table td{border:1px solid #e2e8f0;padding:8px 12px;text-align:left}"
        "table.ref-table th{background:#f8fafc;color:#0f172a;font-weight:600}"
        "table.ref-table th.s-bad{background:#fef2f2;color:#991b1b}"
        "table.ref-table th.s-warn{background:#fffbeb;color:#92400e}"
        "table.ref-table th.s-ok{background:#ecfdf5;color:#065f46}"
        "table.ref-table th.s-exc{background:#eff6ff;color:#1d4ed8}"
        "table.ref-table tr.total td{background:#eff6ff;color:#1d4ed8;font-weight:700}"
        ".explain-block h4{margin:18px 0 6px;font-size:14px;color:#0f172a;font-weight:700;letter-spacing:-0.1px}"
        ".explain-block h4 .pill{display:inline-block;background:#eff6ff;color:#1d4ed8;padding:1px 8px;border-radius:999px;font-size:11px;font-weight:600;margin-left:6px;vertical-align:middle}"
        ".badge{display:inline-flex;align-items:center;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;margin:0 3px}"
        ".b-bad{background:#fef2f2;color:#991b1b}"
        ".b-warn{background:#fffbeb;color:#92400e}"
        ".b-ok{background:#ecfdf5;color:#065f46}"
        ".b-exc{background:#eff6ff;color:#1d4ed8}"
        "table.dataTable{background:#ffffff !important;color:#0f172a !important;border-radius:10px;overflow:hidden;border:1px solid #e2e8f0}"
        "table.dataTable thead th{background:#f8fafc !important;color:#0f172a !important;border:none !important;border-bottom:1px solid #e2e8f0 !important;padding:12px 10px}"
        "table.dataTable tbody td{background:#ffffff !important;border-color:#f1f5f9 !important;color:#1e293b !important}"
        "table.dataTable tbody tr:hover td{background:#f8fafc !important}"
        ".dataTables_wrapper{color:#475569 !important;margin-top:10px}"
        ".dataTables_wrapper .dataTables_filter input,.dataTables_wrapper .dataTables_length select{background:#ffffff;color:#0f172a;border:1px solid #e2e8f0;border-radius:6px;padding:4px 8px;margin-left:6px}"
        ".dataTables_wrapper .dataTables_paginate .paginate_button{color:#475569 !important;border:1px solid transparent !important;border-radius:6px !important;margin:0 2px}"
        ".dataTables_wrapper .dataTables_paginate .paginate_button.current{background:#2563eb !important;color:white !important;border:none !important}"
        ".dataTables_wrapper .dataTables_paginate .paginate_button:hover{background:#f1f5f9 !important;color:#0f172a !important;border:1px solid #e2e8f0 !important}"
        ".footer-bar{display:flex;justify-content:space-between;gap:12px;align-items:center;padding-top:20px;margin-top:28px;border-top:1px solid #e2e8f0;color:#64748b;font-size:13px;flex-wrap:wrap}"
        ".ic{flex:0 0 auto;stroke:currentColor}"
        ".ref-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-top:10px}"
        ".ref-scroll table.ref-table{margin-top:0;min-width:520px}"
        ".dataTables_wrapper{overflow-x:auto;-webkit-overflow-scrolling:touch}"
        "body{overflow-x:hidden}"
        "img,svg{max-width:100%}"
        "@media(max-width:960px){.grid{grid-template-columns:1fr}.insights{grid-template-columns:1fr}}"
        "@media(max-width:640px){"
            "body{padding:18px 12px 32px}"
            ".title{font-size:20px}"
            ".subtitle{font-size:12px}"
            ".header{flex-direction:column;align-items:stretch;gap:12px;padding-bottom:16px;margin-bottom:18px}"
            ".actions{flex-direction:row;width:100%}"
            ".actions .btn{flex:1;justify-content:center;padding:10px 12px;font-size:13px}"
            ".cards{grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:20px}"
            ".card{padding:12px 14px}"
            ".card-value{font-size:22px}"
            ".card-label{font-size:10px;letter-spacing:.06em}"
            ".card-sub{font-size:11px}"
            ".panel{padding:8px;border-radius:12px}"
            ".section-title{margin:24px 4px 10px;font-size:11px}"
            ".section-head{font-size:15px}"
            ".explain-block{padding:14px 16px;border-radius:12px}"
            ".explain-block p,.explain-block li{font-size:13px}"
            ".formula{font-size:12px;word-break:break-word}"
            ".insight{padding:10px 12px;font-size:13px}"
            ".footer-bar{flex-direction:column;align-items:flex-start;gap:4px;font-size:12px}"
        "}"
        "@media(max-width:420px){"
            ".cards{grid-template-columns:repeat(2,1fr)}"
            ".card-chip{display:none}"
            ".card-value{font-size:20px;letter-spacing:-.3px}"
            ".brand-icon{width:38px;height:38px;border-radius:10px}"
            ".title{font-size:18px}"
            ".chip{font-size:11px}"
        "}"
    )

    js = (
        "function downloadHTML(){"
        " var b=document.getElementById('downloadBtn'); b.disabled=true; b.innerText='Lädt...';"
        " var sep=window.location.search? '&' : '?';"
        " fetch(window.location.pathname + window.location.search + sep + 'download=true')"
        "  .then(function(r){ if(!r.ok) throw new Error('net'); return r.blob(); })"
        "  .then(function(blob){ var url=URL.createObjectURL(blob);"
        "    var a=document.createElement('a'); a.href=url; a.download='clan_activity.html';"
        "    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);"
        "    b.disabled=false; b.innerText='HTML herunterladen'; })"
        "  .catch(function(){ alert('Download fehlgeschlagen.');"
        "    b.disabled=false; b.innerText='HTML herunterladen'; });"
        "}"
        "$(document).ready(function(){"
        " $('#top5_table').DataTable({pageLength:5,paging:false,searching:false,info:false});"
        " $('#bottom5_table').DataTable({pageLength:5,paging:false,searching:false,info:false});"
        " $('#full_table').DataTable({pageLength:10,lengthMenu:[5,10,25,50],paging:true,searching:true});"
        "});"
    )

    body_head = (
        '<div class="header">'
        '<div class="brand">'
        '<div class="brand-icon">' + ic('shield', 24) + '</div>'
        '<div>'
        '<h1 class="title">Clan-Aktivitäts-Dashboard</h1>'
        '<div class="subtitle">'
        '<span class="chip">' + safe_tag + '</span>'
        '<span class="meta">Stand ' + current_time + ' · ' + str(n) + ' Mitglieder</span>'
        '</div></div></div>'
        '<div class="actions">'
        '<a class="btn btn-secondary" href="/">' + ic('back', 16) + 'Startseite</a>'
        '<button id="downloadBtn" class="btn btn-success" onclick="downloadHTML()">'
        + ic('download', 16) + 'HTML herunterladen</button>'
        '</div></div>'
    )

    dashboard_grid = (
        '<div class="grid">'
        '<div class="panel full">' + scatter_div + '</div>'
        '<div class="panel">' + don_div + '</div>'
        '<div class="panel">' + hist_div + '</div>'
        '<div class="panel">' + bubble_div + '</div>'
        '<div class="panel">' + th_div + '</div>'
        '<div class="panel">' + role_div + '</div>'
        '<div class="panel full">' + tree_div + '</div>'
        '</div>'
    )

    tables_section = (
        '<div class="section-title">' + ic('bar', 14) + '<span>Rangliste</span></div>'
        '<div class="panel" style="padding:18px 22px;">'
        + top_5_html + bottom_5_html + full_table_html +
        '</div>'
    )

    full_html = (
        '<!DOCTYPE html><html lang="de"><head>'
        '<meta charset="utf-8" />'
        '<meta name="viewport" content="width=device-width,initial-scale=1" />'
        '<title>Clan-Aktivität · ' + safe_tag + '</title>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
        '<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.css">'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">'
        '<script src="https://code.jquery.com/jquery-3.5.1.js"></script>'
        '<script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.js"></script>'
        '<style>' + css + '</style>'
        '</head><body>'
        + body_head
        + cards_html
        + '<div class="section-title">' + ic('lightbulb', 14) + '<span>Interpretation</span></div>'
        + interp_panel
        + '<div class="section-title">' + ic('bar', 14) + '<span>Dashboard</span></div>'
        + dashboard_grid
        + tables_section
        + '<div class="section-title">' + ic('book', 14) + '<span>Erklärung &amp; Orientierung</span></div>'
        + explain_deep
        + '<div class="footer-bar"><div>Daten vom: ' + current_time + '</div>'
        '<div>SOLUNA · Clan-Aktivitäts-Dashboard · ' + safe_tag + '</div></div>'
        '<script>' + js + '</script>'
        '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>'
        '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>'
        '<script>if(window.renderMathInElement){renderMathInElement(document.body,{delimiters:[{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],ignoredTags:["script","noscript","style","textarea","pre","code","option","svg"],throwOnError:false,strict:"ignore"});}</script>'
        '</body></html>'
    )

    return full_html


def normalize_clan_tag(tag: str) -> str:
    tag = tag.strip().upper().replace(' ', '')
    if not tag.startswith('#'):
        tag = '#' + tag
    return tag

async def generate_html_content(clan_tag: str = CLAN_TAG):
    """
    Generiert den HTML-Inhalt für die Clan-Aktivitätsseite.
    """
    # Überprüfen, ob E-Mail und Passwort gesetzt sind
    if not COC_EMAIL or not COC_PASSWORD:
        raise ValueError("COC_EMAIL oder COC_PASSWORD ist nicht gesetzt.")

    # coc.py Client initialisieren
    async with coc.Client() as coc_client:
        try:
            await coc_client.login(COC_EMAIL, COC_PASSWORD)
        except coc.InvalidCredentials as error:
            raise ValueError(f"Ungültige Anmeldedaten: {error}")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Start der Datenabfrage für Clan {clan_tag}...")
        members = await get_clan_members(clan_tag, coc_client)

        if not members:
            raise ValueError("Keine Mitgliederinformationen abgerufen.")

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
                    'trophies': 0, 'best_trophies': 0,
                    'donations': 0, 'donationsReceived': 0,
                    'attackWins': 0, 'defenseWins': 0, 'warStars': 0,
                    'townHall': 0, 'expLevel': 0, 'clanRank': 0,
                    'role': 'Mitglied', 'league': 'Unranked',
                })

        print("\nErstelle den interaktiven Plot mit Plotly...")
        html_content = create_interactive_activity_plot(
            detailed_members,
            clan_tag=clan_tag,
            donation_weight=DONATION_WEIGHT,
            donation_received_weight=DONATION_RECEIVED_WEIGHT,
            attack_win_weight=ATTACK_WIN_WEIGHT,
            trophy_scale=TROPHY_SCALE,
            attack_base_weight=ATTACK_BASE_WEIGHT
        )
        print("Interaktiver Plot erfolgreich erstellt.")

        return html_content

@app.get("/clan-activity")
async def clan_activity(
    download: bool = Query(False, description="Setze auf true, um die HTML als Download zu erhalten"),
    clan_tag: str = Query(None, description="Optionaler Clan-Tag, z.B. #2LUVL2QGL"),
):
    """
    Hauptfunktion, die den Workflow steuert und das Ergebnis entweder als HTML anzeigt oder zum Download anbietet.
    """
    tag = normalize_clan_tag(clan_tag) if clan_tag else CLAN_TAG
    try:
        html_content = await generate_html_content(tag)
    except ValueError as e:
        return HTMLResponse(content=str(e), status_code=500)

    if download:
        # Verwende StringIO, um den HTML-Inhalt als Datei zu behandeln
        buffer = StringIO(html_content)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="text/html",
            headers={
                "Content-Disposition": "attachment; filename=clan_activity_soluna.html"
            }
        )
    else:
        return HTMLResponse(content=html_content, status_code=200)

# Mangum Handler hinzufügen für serverlose Umgebungen wie Vercel
handler = Mangum(app)