import streamlit as st
from db import SessionLocal
from models import Eventos, Ministerios, Participantes, Escalas, Funcoes, participante_funcao, Indisponibilidades
import pandas as pd

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Editar Escalas")

igreja_id = st.session_state.igreja

# Buscar dados da igreja
eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).all()
ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()
funcoes = session.query(Funcoes).filter_by(igreja_id=igreja_id).all()

# Selectbox de evento e ministério
evento = st.selectbox(
    "Evento",
    options=[None] + [e.id for e in eventos],
    format_func=lambda x: "Selecione..." if x is None else f"{next(e.nome for e in eventos if e.id == x)} - {next(e.data.strftime('%d/%m/%Y') for e in eventos if e.id == x)} - {next(e.hora.strftime('%H:%M') if e.hora else 'Não especificada' for e in eventos if e.id == x)}"
)

ministerio = st.selectbox(
    "Ministério (opcional)",
    options=[None] + [m.id for m in ministerios],
    format_func=lambda x: "Todos" if x is None else next(m.nome for m in ministerios if m.id == x)
)

# Inicializar state com escalas do evento
if evento:
    escalas_db = session.query(Escalas).filter_by(evento_id=evento, igreja_id=igreja_id).all()
    if "lista_participante_escala_funcao" not in st.session_state:
        st.session_state.lista_participante_escala_funcao = {
            esc.participante_id: esc.funcao_id for esc in escalas_db
        }

    # Seleção de participante e função
    # Seleção de participante
participante = st.selectbox(
    "Participante",
    options=[p.id for p in participantes],
    format_func=lambda x: next(p.nome for p in participantes if p.id == x)
)

# Verificar impedimentos e duplicidade
if participante and evento:
    evento_obj = session.query(Eventos).get(evento)

    # 1. Verificar indisponibilidade considerando intervalo de horas
    indisponibilidades = session.query(Indisponibilidades).filter_by(
        participante_id=participante,
        igreja_id=igreja_id,
        data=evento_obj.data
    ).all()

    for ind in indisponibilidades:
        if ind.hora_inicio and ind.hora_fim and evento_obj.hora:
            if ind.hora_inicio <= evento_obj.hora <= ind.hora_fim:
                st.warning(
                    f"⚠️ O participante está indisponível em "
                    f"{evento_obj.data.strftime('%d/%m/%Y')} "
                    f"das {ind.hora_inicio.strftime('%H:%M')} às {ind.hora_fim.strftime('%H:%M')}."
                )
        elif evento_obj.hora is None:
            # Caso o evento não tenha hora definida, considerar indisponível no dia inteiro
            st.warning(
                f"⚠️ O participante está indisponível em {evento_obj.data.strftime('%d/%m/%Y')}."
            )

    # 2. Verificar se já está escalado
    ja_escalado = session.query(Escalas).filter_by(
        evento_id=evento,
        participante_id=participante,
        igreja_id=igreja_id
    ).first()

    if ja_escalado:
        st.info("ℹ️ Este participante já está escalado para este evento.")
    funcao_participante = session.query(participante_funcao).filter_by(participante_id=participante).all()
    funcao = st.selectbox(
        "Função",
        options=[f.funcao_id for f in funcao_participante],
        format_func=lambda x: session.query(Funcoes).get(x).nome if session.query(Funcoes).get(x) else ""
    )

    # Botões
    if st.button("Adicionar"):
        st.session_state.lista_participante_escala_funcao[participante] = (funcao, ministerio)

    if st.button("Retirar"):
        if participante in st.session_state.lista_participante_escala_funcao:
            del st.session_state.lista_participante_escala_funcao[participante]

    # Mostrar tabela
    dados_convertidos = [
        {
            "Participante": session.query(Participantes).get(p_id).nome,
            "Função": session.query(Funcoes).get(f_id).nome if f_id else "",
            "Ministério": session.query(Ministerios).get(m_id).nome if m_id else "-"
        }
        for p_id, (f_id, m_id) in st.session_state.lista_participante_escala_funcao.items()
        if ministerio is None or m_id == ministerio
    ]
    st.dataframe(pd.DataFrame(dados_convertidos, columns=["Participante", "Função", "Ministério"]), width="stretch")

    descricao = st.text_area("Descrição da escala (opcional)", height=200)

    # Salvar alterações
    if st.button("Salvar alterações"):
        try:
            # Apagar escalas antigas do evento
            session.query(Escalas).filter_by(evento_id=evento, igreja_id=igreja_id).delete()

            # Recriar com base no state
            for p_id, (f_id, m_id) in st.session_state.lista_participante_escala_funcao.items():
                nova = Escalas(
                    evento_id=evento,
                    ministerio_id=m_id,
                    participante_id=p_id,
                    funcao_id=f_id,
                    igreja_id=igreja_id,
                    descricao=descricao
                )
                session.add(nova)

            session.commit()
            st.success("Escala atualizada com sucesso!")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao salvar: {e}")