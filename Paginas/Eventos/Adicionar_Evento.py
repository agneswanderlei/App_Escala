import streamlit as st
from db import SessionLocal
from models import Eventos

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Cadastro de Eventos")


with st.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do evento")
    with st.container(horizontal=True):
        data = st.date_input("Data do evento", format="DD/MM/YYYY", value=None)
        hora = st.time_input("Hora do evento", value=None, step=300)
    descricao = st.text_area("Descrição do evento (opcional)", height=200)


    salvar = st.form_submit_button("Cadastrar", type="primary")

    if salvar:
        try:
            novo_evento = Eventos(
                nome=nome,
                data=data,
                hora=hora,
                descricao=descricao,
                igreja_id=st.session_state.igreja
            )

            session.add(novo_evento)
            session.commit()

            st.success(f"Evento '{novo_evento.nome}' cadastrado com sucesso!")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao cadastrar Evento: {e}")
        finally:
            session.close()