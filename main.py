import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsbombpy import sb
from mplsoccer import Pitch

# Configuración básica de la página
st.set_page_config(page_title="Visualizador de Pases", layout="centered")

st.title("Visualizador de Pases en Vivo")
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSGm_KqdUINwCyCNhCosSh1VuJ0VgqCYs3Qd5ooAfaWDQ5n4Lc3DOtrx0&s=10", width=300)

# 1. Cargar las ediciones disponibles del Mundial
@st.cache_data
def get_world_cups():
    comps = sb.competitions()
    wc_comps = comps[comps['competition_name'] == 'FIFA World Cup'].copy()
    wc_comps.sort_values(by='season_name', ascending=False, inplace=True)
    return wc_comps

# 2. Cargar partidos de una edición específica
@st.cache_data
def get_matches_for_edition(competition_id, season_id):
    df_matches = sb.matches(competition_id=competition_id, season_id=season_id)
    df_matches['label'] = (
        df_matches['home_team'] + " " + 
        df_matches['home_score'].fillna(0).astype(int).astype(str) + " vs " + 
        df_matches['away_score'].fillna(0).astype(int).astype(str) + " " + 
        df_matches['away_team'] + " (" + 
        df_matches['competition_stage'] + ")"
    )
    return df_matches[['match_id', 'label']].sort_values('label')

# 3. Cargar y procesar los pases del partido seleccionado
@st.cache_data
def load_data(match_id):
    events = sb.events(match_id=match_id)
    variables = ['minute', 'second', 'period', 'location', 'pass_end_location', 
                 'player', 'pass_recipient', 'team', 'type']
    
    passes = events[variables]
    final = passes[passes['type'] == 'Pass'].dropna(subset=['location', 'pass_end_location']).copy()
    
    final['x0'] = final.location.apply(lambda x: x[0])
    final['y0'] = final.location.apply(lambda x: x[1])
    final['x1'] = final.pass_end_location.apply(lambda x: x[0])
    final['y1'] = final.pass_end_location.apply(lambda x: x[1])
    final.drop(columns=['location', 'pass_end_location'], inplace=True)
    return final

# --- Selección de Datos en la UI ---

world_cups = get_world_cups()

# Primer menú desplegable: Edición del Mundial
selected_season = st.selectbox(
    "1. Selecciona la edición del Mundial:", 
    world_cups['season_name'].tolist()
)

# Obtener IDs correspondientes a la edición elegida
selected_wc = world_cups[world_cups['season_name'] == selected_season].iloc[0]
comp_id = int(selected_wc['competition_id'])
season_id = int(selected_wc['season_id'])

# Segundo menú desplegable: Partidos de esa edición
matches = get_matches_for_edition(comp_id, season_id)
selected_match_label = st.selectbox(
    "2. Selecciona el partido:", 
    matches['label'].tolist()
)

# ID del partido seleccionado
match_id = matches[matches['label'] == selected_match_label]['match_id'].values[0]

# Carga de datos del partido
with st.spinner("Cargando pases del partido..."):
    final = load_data(match_id)

# --- Visualización ---

min_minuto = int(final['minute'].min())
max_minuto = int(final['minute'].max())

minuto = st.slider("Selecciona el minuto:", min_value=min_minuto, max_value=max_minuto, value=min_minuto)

pitch = Pitch(pitch_color='grass', line_color='white', stripe=True)
fig, ax = pitch.draw()

df_minuto = final[final.minute == minuto]

if not df_minuto.empty:
    sns.scatterplot(
        data=df_minuto, 
        x='x0', y='y0', 
        ax=ax, 
        hue='team', 
        s=100
    )
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2)
else:
    ax.set_title(f"Sin pases registrados en el minuto {minuto}", color="white")

st.pyplot(fig)
