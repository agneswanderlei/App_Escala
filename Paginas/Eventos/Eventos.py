import streamlit as st
from db import SessionLocal
from models import Eventos, Escalas, DescricaoEscala
import pandas as pd
import datetime
from streamlit_calendar import calendar
from Paginas.Eventos.modal_eventos import detalhes
st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Visualizar Eventos")

igreja_id = st.session_state.get("igreja")
perfil = st.session_state.get("perfil")

# --- Data de hoje ---
hoje = datetime.date.today()

# --- Buscar eventos conforme perfil, apenas futuros ---
if perfil == 'Supervisor':
    eventos = session.query(Eventos).order_by(Eventos.data.asc()).all()
    escalas = session.query(Escalas).all()
else:
    eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).order_by(Eventos.data.asc()).all()
    escalas = session.query(Escalas).filter_by(igreja_id=igreja_id).all()
if not eventos:
    st.warning("Nenhum evento encontrado.")
    st.stop()

# --- Filtros ---
with st.expander("Filtros"):
    with st.container(horizontal=True):
        nome_filtro = st.text_input("Filtrar por nome do evento:")
        nome_participante = st.text_input("Filtrar por participante")
    with st.container(horizontal=True):
        data_inicial = st.date_input("Data Inicial:", value=None, format="DD/MM/YYYY")
        data_final = st.date_input("Data Final:", value=None, format="DD/MM/YYYY")

    # Filtro por nome do evento
    if nome_filtro and nome_filtro.strip():
        eventos = [e for e in eventos if nome_filtro.lower() in e.nome.lower()]

    # Filtro por participante
    if nome_participante and nome_participante.strip():
        eventos = [
            e for e in eventos
            if any(
                nome_participante.lower() in escala.participante.nome.lower()
                for escala in e.escalas if escala.participante
            )
        ]

    # Filtro por data inicial/final
    if data_inicial and data_final:
        eventos = [e for e in eventos if data_inicial <= e.data <= data_final]
    elif data_inicial:
        eventos = [e for e in eventos if e.data >= data_inicial]
    elif data_final:
        eventos = [e for e in eventos if e.data <= data_final]

    if not eventos:
        st.warning("Nenhum evento encontrado com os filtros aplicados.")
        st.stop()

# Converter eventos para o formato do FullCalendar
eventos_data = [
    {
        "title": e.nome,
        "start": e.data.strftime("%Y-%m-%d") + ("T" + e.hora.strftime("%H:%M") if e.hora else ""),
        "end": e.data.strftime("%Y-%m-%d") + ("T" + e.hora.strftime("%H:%M") if e.hora else ""),
        "backgroundColor": "#4CAF50",  # cor personalizada
        "borderColor": "#388E3C",
        "extendedProps": {  # Adicionar dados extras aqui
            "id": e.id,
            "descricao": e.descricao if hasattr(e, 'descricao') else '-',
            "igreja": e.igreja.nome if hasattr(e, 'igreja') else '-',
            "data_formatada": e.data.strftime('%d/%m/%Y'),
            "hora_formatada": e.hora.strftime('%H:%M') if e.hora else '-'
        }
    }
    for e in eventos
]

# Renderizar calendário
calendar_response = calendar(
    events=eventos_data,
    options={
        "initialView": "listMonth",
        "locale": "pt-br",
        "firstDay": 1,
        "eventDisplay": "block",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth"
        }
    }
)

# Capturar clique no evento
if calendar_response and "eventClick" in calendar_response:
    evento = calendar_response["eventClick"]["event"]
    evento_id = evento['extendedProps']['id']
    escala_evento = session.query(Escalas).filter_by(evento_id=evento_id).all()
    descricao_escala = session.query(DescricaoEscala).filter_by(evento_id=evento_id).all()
    # Abrir modal com @dialog
    @st.dialog("Detalhes do Evento", width='medium')
    def mostrar_detalhes():
        detalhes(evento=evento, escalas=escala_evento, descricao=descricao_escala) 
    
    mostrar_detalhes()

session.close()