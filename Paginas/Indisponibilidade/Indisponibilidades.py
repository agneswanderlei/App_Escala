import streamlit as st
from db import SessionLocal
from models import Indisponibilidades, Participantes, Ministerios

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📅 Lista de Indisponibilidades")

igreja_id = st.session_state.get("igreja")
perfil = st.session_state.get('perfil')

# --- Buscar participantes conforme perfil ---
if perfil == 'Supervisor':
    participantes = session.query(Participantes).all()
elif perfil == 'Administrador':
    participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()
else:
    participantes = session.query(Participantes).filter_by(usuario_id=st.session_state.get('user_id')).all()

if not participantes:
    st.warning("Nenhum participante cadastrado ainda.")
    st.stop()

# --- Filtro por ministério ---
ministerios = {m.nome for p in participantes for m in p.ministerios}
ministerio_selecionado = st.multiselect("Filtrar por ministério", options=sorted(ministerios))

if ministerio_selecionado:
    participantes = [
        p for p in participantes
        if any(m.nome in ministerio_selecionado for m in p.ministerios)
    ]

if not participantes:
    st.info("Nenhum participante encontrado com esse filtro.")
    st.stop()

# --- Select participante ---
ids_part = [p.id for p in participantes]
id_selecionado = st.selectbox(
    'Selecione o participante',
    options=ids_part,
    format_func=lambda x: f"{x} - {next((p.nome for p in participantes if p.id == x), '')}"
)

# --- Query base de indisponibilidades ---
query_ind = session.query(Indisponibilidades).filter_by(participante_id=id_selecionado)

# --- Filtros de data ---
with st.expander("🔎 Filtros"):
    data_inicial = st.date_input("Data inicial", format='DD/MM/YYYY')
    data_final = st.date_input("Data final", format="DD/MM/YYYY")

if data_inicial:
    query_ind = query_ind.filter(Indisponibilidades.data >= data_inicial)
if data_final:
    query_ind = query_ind.filter(Indisponibilidades.data <= data_final)

indisponibilidades = query_ind.order_by(Indisponibilidades.data.asc()).all()

# --- Montar dados para tabela ---
dados = []
for p in indisponibilidades:
    dados.append({
        "ID": p.id,
        "Participante":p.participante.nome if p.participante else "",
        "Data": p.data.strftime('%d/%m/%Y'),
        "Hora inicial": p.hora_inicio.strftime('%H:%M') if p.hora_inicio else "",
        "Hora final": p.hora_fim.strftime('%H:%M') if p.hora_fim else "",
        "Motivo": p.motivo
    })

st.dataframe(dados)

session.close()