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

# Cargar todos los partidos de los Mundiales disponibles en StatsBomb
@st.cache_data
def get_world_cup_matches():
    comps = sb.competitions()
    wc_comps = comps[comps['competition_name'] == 'FIFA World Cup']
    
    matches_list = []
    for _, row in wc_comps.iterrows():
        matches = sb.matches(competition_id=row['competition_id'], season_id=row['season_id'])
        matches_list.append(matches)
        
    df_matches = pd.concat(matches_list, ignore_index=True)
    
    # Crear etiqueta descriptiva para el dropdown
    df_matches['label'] = (
        df_matches['season'].astype(str) + " - " + 
        df_matches['home_team'] + " " + df_matches['home_score'].fillna(0).astype(int).astype(str) + 
        " vs " + 
        df_matches['away_score'].fillna(0).astype(int).astype(str) + " " + df_matches['away_team'] + 
        " (" + df_matches['competition_stage'] + ")"
    )
    return df_matches[['match_id', 'label']].sort_values('label')

# Cargar y procesar los datos del partido seleccionado
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

# Selector de Partido
with st.spinner("Cargando lista de partidos del Mundial..."):
    wc_matches = get_world_cup_matches()

selected_match_label = st.selectbox("Selecciona un partido del Mundial:", wc_matches['label'])
match_id = wc_matches[wc_matches['label'] == selected_match_label]['match_id'].values[0]

# Carga de eventos del partido seleccionado
with st.spinner("Cargando pases del partido..."):
    final = load_data(match_id)

# Interactividad: slider de minuto
min_minuto = int(final['minute'].min())
max_minuto = int(final['minute'].max())

minuto = st.slider("Selecciona el minuto:", min_value=min_minuto, max_value=max_minuto, value=min_minuto)

# Gráfico con mplsoccer y seaborn
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

# Renderizar el gráfico en Streamlit
st.pyplot(fig)
