import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models_creed import Presos, Usuarios

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout='centered')
session = SessionLocal()

# -----Buscar Usuarios------
if st.session_state.perfil == "Admin":
    usuarios = session.query(Usuarios).all()
elif st.session_state.perfil == "Gerente":
    usuarios = session.query(Usuarios).filter(Usuarios.perfil != 'Admin').all()
else:
    usuarios = session.query(Usuarios).filter(Usuarios.username == st.session_state.username).all()
ids = [u.id for u in usuarios]
id_selecionado = st.selectbox('Usuário', ids,help='"🔍 Buscar Usuário"', placeholder='Digite o usuário.',format_func=lambda x: f'{x} - {next(p.username for p in usuarios if p.id==x)}')
usuario = session.query(Usuarios).filter(Usuarios.id==id_selecionado).first()

# UI da página
st.title("📋 Editar Senha")

if usuario:
    with st.form("form_senha"):
        nome = st.text_input("Nome completo", disabled=True, value=usuario.nome)
        username = st.text_input("Usuário", placeholder='Digite sua matrícula sem o hifen.', disabled=True,value=usuario.username)
        password = st.text_input("Senha", type="password")
        confirmar = st.text_input("Confirmar senha", type="password")
        enviar = st.form_submit_button("Atualizar", key='warning')

        if enviar:
            if password != confirmar:
                st.warning("🔁 As senhas não coincidem.")
            elif not nome or not username or not password:
                st.warning("📌 Todos os campos são obrigatórios.")
            else:
                try:

                    senha_hash = stauth.Hasher.hash(password)
                    username = username.replace('-', '').strip()
                    usuario.password=senha_hash
                    session.commit()
                    st.success('Usuario atualizado com sucesso!')
                except Exception as e:
                    session.rollback()
                    st.error(f'Não foi possível atualizar usuário: {e}')
                finally:
                    session.close()
else:
    st.warning('Usuário não encontrado!')