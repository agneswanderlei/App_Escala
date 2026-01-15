import streamlit as st
from db import SessionLocal
from models import Eventos, Ministerios, Participantes, Escalas, Funcoes, participante_funcao, Indisponibilidades
import pandas as pd

st.set_page_config(layout='centered')
with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
session = SessionLocal()

st.title("📋 Editar Escalas")

igreja_id = st.session_state.igreja
if 'lista_participante_escala_funcao' not in st.session_state:
    st.session_state.lista_participante_escala_funcao = {}

# Buscar dados da igreja
ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).all()
funcoes = session.query(Funcoes).filter_by(igreja_id=igreja_id).all()
participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()

with st.container(border=True):
    # Selectbox de evento e ministério
    with st.container(horizontal=True, vertical_alignment='bottom'):
        evento = st.selectbox(
            'Eventos',
            options=[e.id for e in eventos],
            format_func=lambda x: next(f"{e.nome} - {e.data.strftime('%d/%m/%Y')} - {e.hora.strftime('%H:%M')}" for e in eventos if e.id == x),
            index=None
        )
        ministerio = st.selectbox(
            'Ministérios',
            options=[m.id for m in ministerios],
            format_func= lambda x: next(m.nome for m in ministerios if m.id == x),
            index=None
        )

    # Inicializar state com escalas do evento
    if evento:
        escalas_db = session.query(Escalas).filter_by(igreja_id=igreja_id, evento_id=evento).all()
        
        st.session_state.lista_participante_escala_funcao = {
            esc.id: (esc.participante_id, esc.funcao_id, esc.ministerio_id, esc.descricao or "")
            for esc in escalas_db
        }

    else:
        st.info('Selecione um evento.')
    ## Seleção de participante e função
    # Seleção de participante
    with st.container(horizontal=True, vertical_alignment='bottom'):
        participante = st.selectbox(
            'Participantes',
            options= [p.id for p in participantes],
            format_func= lambda x: next(p.nome for p in participantes if p.id == x)
        )
        funcao_db = session.query(participante_funcao).filter_by(participante_id=participante).all()
        funcao = st.selectbox(
            'Função',
            options=[f.funcao_id for f in funcao_db],
            format_func=lambda x: next(f.nome for f in funcoes if f.id == x)
        )
        add = st.button('Adicionar', key='primary')
        if add:
            st.session_state.lista_participante_escala_funcao[participante] = (funcao, ministerio)
        retirar = st.button('Retirar', key='warning')
    # Verificar impedimentos e duplicidade
    conflitos = 0
    if participante and evento:
        evento_obj = session.query(Eventos).get(evento)
        # 1. Verificar indisponibilidade considerando intervalo de horas
        indisponibilidades = session.query(Indisponibilidades).filter_by(
            participante_id = participante,
            igreja_id = igreja_id,
            data = evento_obj.data
        ).all()
        for ind in indisponibilidades:
            if ind.hora_inicio and ind.hora_fim and evento_obj.hora:
                if ind.hora_inicio <= evento_obj.hora <= ind.hora_fim:
                    st.warning(
                        f"⚠️ O participante está indisponível em "
                        f"{evento_obj.data.strftime('%d/%m/%Y')}"
                        f" das {ind.hora_inicio.strftime('%H:%M')} as {ind.hora_fim.strftime('%H:%M')}"
                    )
            elif evento_obj.hora is None:
                st.warning(
                    f"⚠️ O participante está indisponível em "
                    f"{evento_obj.data.strftime('%d/%m/%Y')}"
                )
        # 2. Verificar se já está escalado
        # Preciso ver no banco se o participante já está escalado no evento
        ja_escalado = session.query(Escalas).filter_by(
            igreja_id=igreja_id,
            evento_id=evento,
            participante_id=participante
        ).first()
        if ja_escalado:
            st.info(f'Participante já escalado no ministério {ja_escalado.ministerio.nome}!')
    # dados tabela
    dados_convertidos = [
        {
            'Participantes': session.query(Participantes).get(p_id).nome,
            'Funções': session.query(Funcoes).get(f_id).nome if f_id else "",
            'Ministérios': session.query(Ministerios).get(m_id).nome if m_id else "",
            'Descrição': desc
        }
        for _, (p_id, f_id, m_id, desc) in st.session_state.lista_participante_escala_funcao.items() if ministerio is None or m_id == ministerio
    ]
    dados = pd.DataFrame(
        dados_convertidos,
        columns=['Participantes', 'Funções', 'Ministérios']
    )
    st.dataframe(
        dados,
        width='stretch'
    )
    p_id, f_id, m_id, desc = st.session_state.lista_participante_escala_funcao.get(
        escala_id, (None, None, None, "")
    )

    descricao = st.text_area('Descrição', height=200, value=desc)
    with st.container(horizontal=True):
        atualizar = st.button('Atualizar', key='success')
        deletar = st.button('Deletar', key='danger')