import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Turate Basket U18 Analytics",
    page_icon="🏀",
    layout="wide"
)

# STILE PERSONALIZZATO
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #1a202c !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Verde per i valori delle metriche / KPI */
    [data-testid="stMetricValue"] {
        color: #2e7d32 !important;
        font-weight: bold;
    }
    .stSidebar {
        background-color: #f7fafc;
    }
    </style>
""", unsafe_allow_html=True)

# Helper per renderizzare i grafici Plotly (con testo/numeri nei grafici in NERO)
def render_plotly(fig, height=450):
    fig.update_layout(
        template="plotly_white",
        font=dict(size=12, color="#000000"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_traces(textfont_color="#000000")
    
    # Nasconde completamente la modebar dai grafici
    fig_html = fig.to_html(include_plotlyjs='cdn', auto_play=False, config={'displayModeBar': False})
    components.html(fig_html, height=height, scrolling=False)
    
@st.cache_data
def load_data():
    # 1. Trova il percorso del file Excel
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(BASE_DIR, "Turate_Basket.xlsx"),
        os.path.join(BASE_DIR, "Turate", "Turate_Basket.xlsx"),
        os.path.join(BASE_DIR, "Turate_Basket.xls"),
        os.path.join(BASE_DIR, "Turate", "Turate_Basket.xls"),
    ]

    excel_filename = None
    for path in possible_paths:
        if os.path.exists(path):
            excel_filename = path
            break

    if not excel_filename:
        st.error("Errore: Impossibile trovare il file Excel 'Turate_Basket.xlsx' nella cartella del progetto.")
        st.stop()

    # 2. Legge e processa il file Excel
    xls = pd.ExcelFile(excel_filename)
    sheet_names = xls.sheet_names

    giocatori_sheet = next((s for s in sheet_names if "gioc" in s.lower()), sheet_names[0])
    squadra_sheet = next((s for s in sheet_names if "squad" in s.lower()), sheet_names[1] if len(sheet_names) > 1 else sheet_names[0])

    df_giocatori = pd.read_excel(xls, sheet_name=giocatori_sheet)
    df_squadra = pd.read_excel(xls, sheet_name=squadra_sheet)
    
    df_giocatori.columns = df_giocatori.columns.astype(str).str.strip()
    df_squadra.columns = df_squadra.columns.astype(str).str.strip()
    
    # Formattazione della colonna Data senza orario (GG/MM/AAAA)
    df_squadra["Data"] = pd.to_datetime(df_squadra["Data"]).dt.strftime('%d/%m/%Y')
    
    df_giocatori = df_giocatori[df_giocatori["Giocatori"].astype(str).str.upper() != "TOTALE"].copy()
    
    cols_stats = ["Punti segnati", "2P segnati", "2P tentati", "3P segnati", "3P tentati", "TL segnati", "TL tentati", "Palle perse"]
    for c in cols_stats:
        if c not in df_giocatori.columns:
            df_giocatori[c] = np.nan
        else:
            df_giocatori[c] = pd.to_numeric(df_giocatori[c], errors="coerce")

    # Flag: giocato = True se c'è almeno un dato registrato che sia diverso da 0 e non nullo
    df_giocatori["Ha_Giocato"] = df_giocatori[cols_stats].fillna(0).sum(axis=1) > 0
    
    return df_squadra, df_giocatori

# --- CARICAMENTO DATI EFFETTIVO ---
df_squadra, df_giocatori = load_data()

# --- SIDEBAR & NAVIGAZIONE ---
st.sidebar.title("🏀 Turate Basket U18")
page = st.sidebar.radio("Seleziona Sezione:", ["Game Center (Partita)", "Profilo Giocatore", "Analisi Avanzata & Roster"])

# ---------------------------------------------------------
# TAB 1: GAME CENTER (ANALISI SINGOLA PARTITA)
# ---------------------------------------------------------
if page == "Game Center (Partita)":
    st.title("📊 Game Center — Analisi Singola Gara")
    
    partite_disponibili = df_squadra["Numero partita"].tolist()
    partita_sel = st.sidebar.selectbox(
        "Seleziona Partita:", 
        partite_disponibili,
        format_func=lambda x: f"{df_squadra[df_squadra['Numero partita']==x]['Tipo'].values[0]} vs {df_squadra[df_squadra['Numero partita']==x]['Avversario'].values[0]} ({df_squadra[df_squadra['Numero partita']==x]['Data'].values[0]})"
    )
    
    info_gara = df_squadra[df_squadra["Numero partita"] == partita_sel].iloc[0]
    stats_gara = df_giocatori[df_giocatori["Partita"] == partita_sel].copy()
    
    pts_fatti = info_gara["Punti fatti"]
    pts_subiti = info_gara["Punti subiti"]
    
    # Determina W o L
    esito = "W" if pts_fatti > pts_subiti else ("L" if pts_fatti < pts_subiti else "D")
    esito_label = f"[{esito}] {pts_fatti} - {pts_subiti}"
    
    tot_2pm = stats_gara["2P segnati"].fillna(0).sum()
    tot_2pa = stats_gara["2P tentati"].fillna(0).sum()
    tot_3pm = stats_gara["3P segnati"].fillna(0).sum()
    tot_3pa = stats_gara["3P tentati"].fillna(0).sum()
    tot_ftm = stats_gara["TL segnati"].fillna(0).sum()
    tot_fta = stats_gara["TL tentati"].fillna(0).sum()
    tot_to = stats_gara["Palle perse"].fillna(0).sum()
    
    pct_2p = (tot_2pm / tot_2pa * 100) if tot_2pa > 0 else 0.0
    pct_3p = (tot_3pm / tot_3pa * 100) if tot_3pa > 0 else 0.0
    pct_ft = (tot_ftm / tot_fta * 100) if tot_fta > 0 else 0.0
    
    st.subheader(f"{info_gara['Tipo']} vs **{info_gara['Avversario']}** — {info_gara['Data']}")
    
    # KPI e Risultato con W / L
    c_res, c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(5)
    c_res.metric("Risultato", esito_label, delta=int(pts_fatti - pts_subiti))
    c_kpi1.metric("2P %", f"{pct_2p:.1f}%", f"{int(tot_2pm)}/{int(tot_2pa)}")
    c_kpi2.metric("3P %", f"{pct_3p:.1f}%", f"{int(tot_3pm)}/{int(tot_3pa)}")
    c_kpi3.metric("TL %", f"{pct_ft:.1f}%", f"{int(tot_ftm)}/{int(tot_fta)}")
    c_kpi4.metric("Palle Perse", f"{int(tot_to)}")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("Distribuzione Punti per Giocatore")
        stats_gara_graf = stats_gara[stats_gara["Ha_Giocato"]].copy()
        stats_gara_graf["Punti 2P"] = stats_gara_graf["2P segnati"].fillna(0) * 2
        stats_gara_graf["Punti 3P"] = stats_gara_graf["3P segnati"].fillna(0) * 3
        stats_gara_graf["Punti TL"] = stats_gara_graf["TL segnati"].fillna(0)

        fig_pts = px.bar(
            stats_gara_graf,
            x="Giocatori",
            y=["Punti 2P", "Punti 3P", "Punti TL"],
            title="Punti realizzati per Tipologia",
            labels={"value": "Punti", "variable": "Tipo Tiro"},
            text_auto=True,
            color_discrete_map={
                "Punti 2P": "#3182ce",
                "Punti 3P": "#dd6b20",
                "Punti TL": "#48bb78"
            }
        )
        render_plotly(fig_pts)

    with col_chart2:
        st.subheader("Titolari vs Panchina")
        pts_tit = stats_gara[(stats_gara["Titolare"] == 1) & (stats_gara["Ha_Giocato"])]["Punti segnati"].fillna(0).sum()
        pts_pan = stats_gara[(stats_gara["Titolare"] == 0) & (stats_gara["Ha_Giocato"])]["Punti segnati"].fillna(0).sum()
        
        fig_pie = px.pie(
            names=["Titolari", "Panchina"],
            values=[pts_tit, pts_pan],
            hole=0.4,
            color_discrete_sequence=["#2b6cb0", "#a0aec0"]
        )
        fig_pie.update_traces(textinfo="value+percent", textfont_color="#000000")
        render_plotly(fig_pie)

    # Box Score
    st.subheader("Box Score Completo")
    stats_gara_display = stats_gara.copy()
    
    # Formattazione dati tabella: sostituisce celle vuote/non giocate con N/D
    def fmt_pct(row, seg_col, tent_col):
        if not row["Ha_Giocato"]:
            return "N/D"
        seg = row[seg_col]
        tent = row[tent_col]
        if pd.isna(seg) or pd.isna(tent) or tent == 0:
            return "N/D"
        return f"{(seg / tent * 100):.1f}%"

    def fmt_val(row, col):
        if not row["Ha_Giocato"]:
            return "N/D"
        val = row[col]
        return "N/D" if pd.isna(val) else int(val)

    stats_gara_display["2P %"] = stats_gara_display.apply(lambda r: fmt_pct(r, "2P segnati", "2P tentati"), axis=1)
    stats_gara_display["3P %"] = stats_gara_display.apply(lambda r: fmt_pct(r, "3P segnati", "3P tentati"), axis=1)
    stats_gara_display["TL %"] = stats_gara_display.apply(lambda r: fmt_pct(r, "TL segnati", "TL tentati"), axis=1)

    for col in ["Punti segnati", "2P segnati", "2P tentati", "3P segnati", "3P tentati", "TL segnati", "TL tentati", "Palle perse"]:
        stats_gara_display[col] = stats_gara_display.apply(lambda r, c=col: fmt_val(r, c), axis=1)

    st.dataframe(
        stats_gara_display[[
            "Giocatori", "Titolare", "Punti segnati", 
            "2P segnati", "2P tentati", "2P %", 
            "3P segnati", "3P tentati", "3P %", 
            "TL segnati", "TL tentati", "TL %", "Palle perse"
        ]],
        use_container_width=True
    )

# ---------------------------------------------------------
# TAB 2: PROFILO GIOCATORE
# ---------------------------------------------------------
elif page == "Profilo Giocatore":
    st.title("👤 Scheda Singolo Giocatore")
    
    lista_giocatori = sorted(df_giocatori["Giocatori"].unique())
    giocatore_sel = st.sidebar.selectbox("Seleziona Giocatore:", lista_giocatori)
    
    # Considera solo le gare in cui il giocatore ha effettivamente giocato
    df_gioc = df_giocatori[(df_giocatori["Giocatori"] == giocatore_sel) & (df_giocatori["Ha_Giocato"])].copy()
    
    partite_giocate = len(df_gioc)
    media_pts = df_gioc["Punti segnati"].mean() if partite_giocate > 0 else 0.0
    tot_2pm = df_gioc["2P segnati"].fillna(0).sum()
    tot_2pa = df_gioc["2P tentati"].fillna(0).sum()
    tot_3pm = df_gioc["3P segnati"].fillna(0).sum()
    tot_3pa = df_gioc["3P tentati"].fillna(0).sum()
    tot_ftm = df_gioc["TL segnati"].fillna(0).sum()
    tot_fta = df_gioc["TL tentati"].fillna(0).sum()
    tot_to = df_gioc["Palle perse"].fillna(0).sum()
    media_to = tot_to / partite_giocate if partite_giocate > 0 else 0.0
    
    pct_2p = f"{(tot_2pm / tot_2pa * 100):.1f}%" if tot_2pa > 0 else "N/D"
    pct_3p = f"{(tot_3pm / tot_3pa * 100):.1f}%" if tot_3pa > 0 else "N/D"
    pct_ft = f"{(tot_ftm / tot_fta * 100):.1f}%" if tot_fta > 0 else "N/D"

    st.header(f"Giocatore: **{giocatore_sel}**")
    
    if partite_giocate == 0:
        st.warning("Nessuna partita giocata registrata per questo giocatore.")
    else:
        # 6 Metriche KPI
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Partite Giocate", f"{partite_giocate}")
        c2.metric("Media Punti", f"{media_pts:.1f}")
        c3.metric("2P %", pct_2p, f"{int(tot_2pm)}/{int(tot_2pa)}")
        c4.metric("3P %", pct_3p, f"{int(tot_3pm)}/{int(tot_3pa)}")
        c5.metric("TL %", pct_ft, f"{int(tot_ftm)}/{int(tot_fta)}")
        c6.metric("Palle Perse", f"{int(tot_to)}", f"M: {media_to:.1f}/gara")

        st.markdown("---")
        
        df_gioc = df_gioc.merge(df_squadra[["Numero partita", "Avversario"]], left_on="Partita", right_on="Numero partita")
        
        fig_trend = px.line(
            df_gioc,
            x="Avversario",
            y="Punti segnati",
            markers=True,
            text="Punti segnati",
            title=f"Andamento Punti di {giocatore_sel}",
            color_discrete_sequence=["#2e7d32"]
        )
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=9), textposition="top center", textfont_color="#000000")
        render_plotly(fig_trend)

# ---------------------------------------------------------
# TAB 3: ANALISI AVANZATA & ROSTER
# ---------------------------------------------------------
elif page == "Analisi Avanzata & Roster":
    st.title("📈 Analisi Roster e Progressione Stagionale")
    
    # --- GRAFICO 1: PROGRESSIONE PUNTI SQUADRA ---
    st.subheader("📉 Andamento Punti Squadra nel Corso della Stagione")
    
    df_squadra_sorted = df_squadra.sort_values(by="Numero partita").copy()
    df_squadra_sorted["Esito"] = df_squadra_sorted.apply(
        lambda r: "W" if r["Punti fatti"] > r["Punti subiti"] else "L", axis=1
    )
    df_squadra_sorted["Label_Partita"] = df_squadra_sorted.apply(
        lambda r: f"G{r['Numero partita']}: {r['Avversario']} ({r['Esito']})", axis=1
    )
    
    fig_season = go.Figure()
    
    fig_season.add_trace(go.Scatter(
        x=df_squadra_sorted["Label_Partita"],
        y=df_squadra_sorted["Punti fatti"],
        mode='lines+markers+text',
        name='Punti Fatti',
        text=df_squadra_sorted["Punti fatti"],
        textposition="top center",
        line=dict(color='#2e7d32', width=3),
        marker=dict(size=8)
    ))
    
    fig_season.add_trace(go.Scatter(
        x=df_squadra_sorted["Label_Partita"],
        y=df_squadra_sorted["Punti subiti"],
        mode='lines+markers+text',
        name='Punti Subiti',
        text=df_squadra_sorted["Punti subiti"],
        textposition="bottom center",
        line=dict(color='#e53e3e', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    
    fig_season.update_layout(
        title="Punti Fatti vs Punti Subiti per Partita",
        xaxis_title="Partita",
        yaxis_title="Punti",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    render_plotly(fig_season, height=450)

    st.markdown("---")

    # --- GRAFICO 2: EVOLUZIONE PERCENTUALI DI TIRO ---
    st.subheader("🎯 Evoluzione Percentuali di Tiro nella Stagione")
    
    df_gioc_validi = df_giocatori[df_giocatori["Ha_Giocato"]].copy()

    team_shooting_per_game = df_gioc_validi.groupby("Partita").agg({
        "2P segnati": "sum",
        "2P tentati": "sum",
        "3P segnati": "sum",
        "3P tentati": "sum",
        "TL segnati": "sum",
        "TL tentati": "sum"
    }).reset_index()

    team_shooting_per_game = team_shooting_per_game.merge(
        df_squadra_sorted[["Numero partita", "Label_Partita"]],
        left_on="Partita",
        right_on="Numero partita"
    )

    team_shooting_per_game["2P %"] = (team_shooting_per_game["2P segnati"] / team_shooting_per_game["2P tentati"] * 100).fillna(0).round(1)
    team_shooting_per_game["3P %"] = (team_shooting_per_game["3P segnati"] / team_shooting_per_game["3P tentati"] * 100).fillna(0).round(1)
    team_shooting_per_game["TL %"] = (team_shooting_per_game["TL segnati"] / team_shooting_per_game["TL tentati"] * 100).fillna(0).round(1)

    fig_pct_trend = go.Figure()

    # Linea 2P %
    fig_pct_trend.add_trace(go.Scatter(
        x=team_shooting_per_game["Label_Partita"],
        y=team_shooting_per_game["2P %"],
        mode='lines+markers+text',
        name='2P %',
        text=team_shooting_per_game["2P %"].apply(lambda x: f"{x:.1f}%"),
        customdata=list(zip(team_shooting_per_game["2P segnati"].astype(int), team_shooting_per_game["2P tentati"].astype(int))),
        hovertemplate="<b>2P %</b>: %{y:.1f}% (%{customdata[0]}/%{customdata[1]})<extra></extra>",
        textposition="top center",
        line=dict(color='#3182ce', width=3),
        marker=dict(size=8)
    ))

    # Linea 3P %
    fig_pct_trend.add_trace(go.Scatter(
        x=team_shooting_per_game["Label_Partita"],
        y=team_shooting_per_game["3P %"],
        mode='lines+markers+text',
        name='3P %',
        text=team_shooting_per_game["3P %"].apply(lambda x: f"{x:.1f}%"),
        customdata=list(zip(team_shooting_per_game["3P segnati"].astype(int), team_shooting_per_game["3P tentati"].astype(int))),
        hovertemplate="<b>3P %</b>: %{y:.1f}% (%{customdata[0]}/%{customdata[1]})<extra></extra>",
        textposition="bottom center",
        line=dict(color='#dd6b20', width=3),
        marker=dict(size=8)
    ))

    # Linea TL %
    fig_pct_trend.add_trace(go.Scatter(
        x=team_shooting_per_game["Label_Partita"],
        y=team_shooting_per_game["TL %"],
        mode='lines+markers+text',
        name='TL %',
        text=team_shooting_per_game["TL %"].apply(lambda x: f"{x:.1f}%"),
        customdata=list(zip(team_shooting_per_game["TL segnati"].astype(int), team_shooting_per_game["TL tentati"].astype(int))),
        hovertemplate="<b>TL %</b>: %{y:.1f}% (%{customdata[0]}/%{customdata[1]})<extra></extra>",
        textposition="top center",
        line=dict(color='#48bb78', width=3),
        marker=dict(size=8)
    ))

    fig_pct_trend.update_layout(
        title="Andamento 2P%, 3P% e TL% di Squadra per Partita",
        xaxis_title="Partita",
        yaxis_title="Percentuale (%)",
        yaxis=dict(range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    render_plotly(fig_pct_trend, height=450)

    st.markdown("---")

    # --- CLASSIFICA ROSTER ---
    st.subheader("🏆 Classifica e Statistiche Roster")
    
    # Raggruppa sia tutti i giocatori per avere l'elenco completo, sia solo quelli con partite giocate
    tutti_giocatori = pd.DataFrame({"Giocatori": sorted(df_giocatori["Giocatori"].unique())})
    
    agg_players = df_gioc_validi.groupby("Giocatori").agg({
        "Partita": "count",
        "Punti segnati": ["sum", "mean"],
        "2P segnati": "sum",
        "2P tentati": "sum",
        "3P segnati": "sum",
        "3P tentati": "sum",
        "TL segnati": "sum",
        "TL tentati": "sum",
        "Palle perse": ["sum", "mean"]
    }).reset_index()
    
    agg_players.columns = [
        "Giocatori", "Partite", "Punti_Tot", "Punti_Media", 
        "2PM", "2PA", "3PM", "3PA", "FTM", "FTA", "TO_Tot", "TO_Media"
    ]
    
    # Merge con tutti i giocatori per non escludere chi ha 0 partite giocate
    roster_summary = tutti_giocatori.merge(agg_players, on="Giocatori", how="left").fillna(0)

    # Calcolo percentuali o N/D
    roster_summary["2P%"] = roster_summary.apply(lambda r: f"{(r['2PM']/r['2PA']*100):.1f}%" if r["2PA"] > 0 else "N/D", axis=1)
    roster_summary["3P%"] = roster_summary.apply(lambda r: f"{(r['3PM']/r['3PA']*100):.1f}%" if r["3PA"] > 0 else "N/D", axis=1)
    roster_summary["TL%"] = roster_summary.apply(lambda r: f"{(r['FTM']/r['FTA']*100):.1f}%" if r["FTA"] > 0 else "N/D", axis=1)

    agg_display = roster_summary.copy()
    agg_display["Partite"] = agg_display["Partite"].astype(int)
    agg_display["Punti_Tot"] = agg_display["Punti_Tot"].astype(int)
    agg_display["TO_Tot"] = agg_display["TO_Tot"].astype(int)
    agg_display["Punti_Media"] = agg_display["Punti_Media"].round(1)
    agg_display["TO_Media"] = agg_display["TO_Media"].round(1)

    # Rinomina colonne per la tabella finale
    agg_display = agg_display.rename(columns={
        "Giocatori": "Giocatore",
        "TO_Tot": "Palle perse totali",
        "TO_Media": "Palle perse media"
    })

    st.dataframe(
        agg_display[["Giocatore", "Partite", "Punti_Tot", "Punti_Media", "2P%", "3P%", "TL%", "Palle perse totali", "Palle perse media"]]
        .sort_values(by=["Partite", "Punti_Tot"], ascending=[False, False]),
        use_container_width=True
    )
