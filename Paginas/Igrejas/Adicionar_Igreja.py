import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Igrejas

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout='centered')
session = SessionLocal()

# UI da página
st.title("📋 Cadastro de Igrejas")

with st.form("form_cadastro"):
    nome = st.text_input("Nome da igreja")
    
    salvar = st.form_submit_button("Cadastrar", key='success')

    if salvar:
        if nome.strip() == "":
            st.error("⚠️ O nome da igreja não pode estar vazio.")
        else:
            try:
                # cria objeto da igreja
                nova_igreja = Igrejas(nome=nome.strip())
                session.add(nova_igreja)
                session.commit()
                st.success(f"Igreja '{nome}' cadastrada com sucesso!")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar igreja: {e}")
            finally:
                session.close()