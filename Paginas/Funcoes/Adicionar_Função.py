import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Funcoes

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout='centered')
session = SessionLocal()

# UI da página
st.title("📋 Cadastro de Funções")

with st.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome da função")
    descricao = st.text_area('Descrição')
    igreja_id = st.session_state.igreja
    salvar = st.form_submit_button("Cadastrar", key='success')

    if salvar:
        if nome.strip() == "":
            st.error("⚠️ O nome da função não pode estar vazio.")
        else:
            try:
                # cria objeto da igreja
                nova_funcao = Funcoes(
                    nome=nome.strip(),
                    descricao=descricao,
                    igreja_id=igreja_id
                )
                session.add(nova_funcao)
                session.commit()
                st.success(f"Função '{nome}' cadastrada com sucesso!")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar Função: {e}")
            finally:
                session.close()