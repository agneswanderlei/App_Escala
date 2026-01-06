import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Usuarios, Igrejas

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(layout='centered')
session = SessionLocal()

# -----Buscar Usuarios------
if st.session_state['perfil'] == 'Supervisor':
    igrejas = session.query(Igrejas).all()
    ids_igrejas = [i.id for i in igrejas]
    igreja_selecionada = st.selectbox(
        'Igreja',
        ids_igrejas,
        help='"🔍 Buscar Igreja"',
        placeholder='Digite a igreja.',
        format_func=lambda x: f'{x} - {next(i.nome for i in igrejas if i.id==x)}'
    )
    usuarios = session.query(Usuarios).filter_by(igreja_id=igreja_selecionada).all()
elif st.session_state['perfil'] == 'Administrador':
    usuarios = session.query(Usuarios).filter_by(igreja_id=st.session_state.igreja).all()
else:
    usuarios = session.query(Usuarios).filter_by(igreja_id=st.session_state.igreja, id=st.session_state['user_id']).all()

ids = [u.id for u in usuarios]

id_selecionado = st.selectbox(
    'Usuário',
    ids,
    help='"🔍 Buscar Usuário"',
    placeholder='Digite o usuário.',
    format_func=lambda x: f'{x} - {next(p.cpf for p in usuarios if p.id==x)}'
)

usuario = session.query(Usuarios).filter(Usuarios.id == id_selecionado).first()

# UI da página
st.title("🔑 Alterar Senha")

if usuario:
    with st.form("form_senha"):
        nome = st.text_input("Nome completo", disabled=True, value=usuario.nome)
        username = st.text_input("Usuário (CPF)", disabled=True, value=usuario.cpf)

        nova_senha = st.text_input("Nova senha", type="password")
        confirmar_senha = st.text_input("Confirmar nova senha", type="password")

        enviar = st.form_submit_button("Atualizar Senha", key='warning')

        if enviar:
            if not nova_senha or not confirmar_senha:
                st.warning("📌 Todos os campos são obrigatórios.")
            elif nova_senha != confirmar_senha:
                st.warning("🔁 As senhas não coincidem.")
            else:
                try:
                    senha_hash = stauth.Hasher.hash(nova_senha)
                    usuario.password = senha_hash
                    session.commit()
                    st.success("Senha atualizada com sucesso! ✅")
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro ao atualizar senha: {e}")
                finally:
                    session.close()
else:
    st.warning("Usuário não encontrado!")