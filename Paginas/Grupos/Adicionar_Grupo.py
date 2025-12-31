import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Ministerios

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout='centered')
session = SessionLocal()

# UI da página
st.title("📋 Cadastro de Grupos/Ministérios")

with st.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do grupo/ministério")
    igreja_id = st.session_state.igreja
    salvar = st.form_submit_button("Cadastrar", key='success')

    if salvar:
        if nome.strip() == "":
            st.error("⚠️ O nome do grupo/ministério não pode estar vazio.")
        else:
            try:
                # cria objeto da igreja
                novo_ministerio = Ministerios(
                    nome=nome.strip(),
                    igreja_id=igreja_id
                )
                session.add(novo_ministerio)
                session.commit()
                st.success(f"Grupo '{nome}' cadastrado com sucesso!")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar Grupo: {e}")
            finally:
                session.close()