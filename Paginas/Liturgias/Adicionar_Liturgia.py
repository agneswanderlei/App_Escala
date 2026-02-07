import streamlit as st
from db import SessionLocal
from models import Eventos, Participantes, Liturgias, MomentosLiturgia
import os, time

st.set_page_config(layout='centered')
session = SessionLocal()
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
if 'momentos_state' not in st.session_state:
    st.session_state.momentos_state = {}
st.title("📋 Criar Liturgia")
igreja_id = st.session_state.igreja
eventos = session.query(Eventos).filter_by(
    igreja_id=igreja_id
).order_by(Eventos.data.asc())
participantes = session.query(Participantes).filter_by(
    igreja_id=igreja_id
)
ids = [e.id for e in eventos]
evento = st.selectbox(
    'Evento',
    options=ids,
    format_func=lambda x: next(f"{e.data.strftime('%d/%m/%Y')} - {e.nome}" for e in eventos if e.id == x)
)
ids_participante = [p.id for p in participantes]
with st.container(border=True):
    nome = st.text_input('Nome da liturgia')
    with st.container(horizontal=True, vertical_alignment='bottom', gap='small', horizontal_alignment='center'):
        col1, col2, col3 = st.columns([1.2,2,2])
        with col1:
            hora = st.time_input('hora', step=60, value=None)
        with col2:
            descricao = st.text_input('Descrição')
        with col3:
            participante = st.multiselect(
            'Responsáveis',
            options=ids_participante,
            format_func=lambda x: next(p.nome for p in participantes if p.id == x)
        )
        add = st.button('Add',key='success')
        deletar = st.button('Del',key='danger')
    if add:
        if participante:
            st.session_state.momentos_state[hora] = (descricao, participante)
    if deletar:
        if hora in st.session_state.momentos_state.keys():
            del st.session_state.momentos_state[hora]
        else:
            st.warning('Selecione a hora correta do momento da liturgia.')
    dados = [{
        "Hora": h.strftime("%H:%M"),
        "Descrição": desc,
        "Responsáveis": ", ".join(
            next((p.nome for p in participantes if p.id == pid), "-") 
            for pid in resp
        ) if resp else "-"
    } for h, (desc, resp) in sorted(st.session_state.momentos_state.items())]
    st.dataframe(dados)
    observacao = st.text_area('Observação')
    salvar = st.button('Salvar', key='primary')
    if salvar:
        try:
            nova_liturgia = Liturgias(
                nome=nome,
                igreja_id=igreja_id,
                evento_id=evento,
                descricao=observacao
            )
            session.add(nova_liturgia)
            session.commit()
            for hora, (desc, responsaveis) in st.session_state.momentos_state.items():
                for pid in responsaveis:
                
                    momento = MomentosLiturgia(
                        horario = hora,
                        descricao = desc,
                        responsavel_id = pid,
                        liturgia_id = nova_liturgia.id
                    )
                    session.add(momento)
            session.commit()
            st.success('Liturgia salva com sucesso!')
            time.sleep(2)
            st.switch_page(os.path.join('Paginas','Eventos','Eventos.py'))
        except Exception as e:
            session.rollback()
            st.warning(f'Não foi possível cadastrar liturgia: {e}')