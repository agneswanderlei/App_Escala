import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Usuarios, Igrejas

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.set_page_config(layout='centered')
session = SessionLocal()
# UI da página
st.title("📋 Cadastro de Usuário")

with st.form("form_cadastro"):
    if st.session_state['perfil'] == 'Supervisor':
        igreja_opcao = st.selectbox("Selecione a Igreja", options=[(i.id, i.nome) for i in session.query(Igrejas).all()], format_func=lambda x: x[1])
        igreja_id = igreja_opcao[0]
    else:
        igreja_id = st.session_state.igreja
    nome = st.text_input("Nome completo")
    cpf = st.text_input("Usuário", placeholder='Digite seu CPF')
    perfil = st.selectbox('Perfil',options=['Administrador','Líder','Auxiliar'],index=None)
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    enviar = st.form_submit_button("Cadastrar", key='success')

    if enviar:
        if senha != confirmar:
            st.warning("🔁 As senhas não coincidem.")
        elif not nome or not cpf or not senha:
            st.warning("📌 Todos os campos são obrigatórios.")
        else:
            try:
                senha_hash = stauth.Hasher.hash(senha)
                cpf = cpf.strip()
                novo_usuario = Usuarios(
                    nome=nome,
                    cpf=cpf,
                    perfil=perfil,
                    password=senha_hash,
                    igreja_id=igreja_id
                )
                session.add(novo_usuario)
                session.commit()
                st.success('Usuário cadastrado com sucesso!',icon='✅')
            except Exception as e:
                session.rollback()
                st.error(f'Não foi possível adicionar usuario: {e}')
            finally:
                session.close()