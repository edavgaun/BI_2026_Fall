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

# Cargar y procesar los datos con caché para acelerar la app
@st.cache_data
def load_data(match_id=3857255):
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

# Carga de datos
with st.spinner("Cargando datos de StatsBomb..."):
    final = load_data()

# Interactividad: reemplazo de ipywidgets por st.slider
min_minuto = int(final['minute'].min())
max_minuto = int(final['minute'].max())

minuto = st.slider("Selecciona el minuto:", min_value=min_minuto, max_value=max_minuto, value=0)

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
