import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Usuarios, Igrejas, Ministerios, usuario_ministerio

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.set_page_config(layout='centered')
session = SessionLocal()


# UI da página
st.title("📋 Cadastro de Usuário")

# with st.form("form_cadastro", clear_on_submit=True):
with st.container(border=True):
    if st.session_state['perfil'] == 'Supervisor':
        igreja_opcao = st.selectbox("Selecione a Igreja", options=[(i.id, i.nome) for i in session.query(Igrejas).all()], format_func=lambda x: x[1])
        igreja_id = igreja_opcao[0]
    else:
        igreja_id = st.session_state.igreja
    nome = st.text_input("Nome completo")
    cpf = st.text_input("Usuário", placeholder='Digite seu CPF')
    perfil = st.selectbox('Perfil',options=['Administrador','Líder','Auxiliar'],index=None)
    ministerios_escolhidos = []
    if perfil == 'Líder':
        ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
        ministerios_escolhidos = st.multiselect(
            'Ministérios',
            options=[m.id for m in ministerios],
            format_func=lambda x: next(m.nome for m in ministerios if m.id == x)
        )
    telefone = st.text_input("Nº do telefone", placeholder='Apenas números! Ex. 81988887777',help='Não precisa colocar parênteses e nem traços ex: (81) 98888-7777')
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    enviar = st.button("Cadastrar", key='success')

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
                    telefone=telefone,
                    password=senha_hash,
                    igreja_id=igreja_id
                )
                for m_id in ministerios_escolhidos:
                    ministerio = session.query(Ministerios).get(m_id)
                    novo_usuario.ministerios.append(ministerio)
                session.add(novo_usuario)
                session.commit()
                st.success('Usuário cadastrado com sucesso!',icon='✅')
            except Exception as e:
                session.rollback()
                st.error(f'Não foi possível adicionar usuario: {e}')
            finally:
                session.close()