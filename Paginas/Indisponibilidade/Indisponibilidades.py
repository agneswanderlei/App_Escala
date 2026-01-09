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
    st.session_state.indisponibilidade = session.query(Indisponibilidades).all()
elif perfil == 'Administrador':
    st.session_state.indisponibilidade = session.query(Indisponibilidades).filter_by(igreja_id=igreja_id).all()
else:
    st.session_state.indisponibilidade = session.query(Indisponibilidades).filter_by(usuario_id=st.session_state.get('user_id')).all()

if not st.session_state.indisponibilidade:
    st.warning("Nenhuma indisponibilidade cadastrada ainda.")
    st.stop()

# --- Filtro por ministério ---
ministerios = {m.nome for ind in st.session_state.indisponibilidade for m in ind.participante.ministerios}
ministerio_selecionado = st.multiselect("Filtrar por ministério", options=sorted(ministerios))
participante = {p.id for ind in st.session_state.indisponibilidade for p in [ind.participante] if not ministerio_selecionado or any(m.nome in ministerio_selecionado for m in p.ministerios)}

participante_selecionado = st.multiselect(
    "Filtrar por participante",
    options=sorted([p.id for ind in st.session_state.indisponibilidade for p in [ind.participante] if p.id in participante]),
    format_func=lambda x: next((p.nome for ind in st.session_state.indisponibilidade for p in [ind.participante] if p.id == x), "")
)


# Aplicar filtros
if ministerio_selecionado:
    st.session_state.indisponibilidade = [ind for ind in st.session_state.indisponibilidade if any(m.nome in ministerio_selecionado for m in ind.participante.ministerios)]
if participante_selecionado:
    st.session_state.indisponibilidade = [ind for ind in st.session_state.indisponibilidade if ind.participante.id in participante_selecionado]
# --- Montar dados para tabela ---
dados = []
for ind in st.session_state.indisponibilidade:
    dados.append({
        "ID": ind.id,
        "Participante": ind.participante.nome if ind.participante else "",
        "Ministério": ", ".join([m.nome for m in ind.participante.ministerios]) if ind.participante else "" ,
        "Data": ind.data.strftime('%d/%m/%Y'),
        "Hora inicial": ind.hora_inicio.strftime('%H:%M') if ind.hora_inicio else "",
        "Hora final": ind.hora_fim.strftime('%H:%M') if ind.hora_fim else "",
        "Motivo": ind.motivo
    })

st.dataframe(dados)

session.close()