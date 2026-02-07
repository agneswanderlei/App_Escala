import streamlit as st
import streamlit_authenticator as stauth
import os
from db import SessionLocal
from models import Usuarios, Igrejas, Ministerios

with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.set_page_config(layout='centered')
session = SessionLocal()



# -----Buscar Usuarios------
if st.session_state['perfil'] == 'Supervisor':
    igrejas = session.query(Igrejas).all()
    ids_igrejas = [i.id for i in igrejas]
    igreja_selecionada = st.selectbox('Igreja', ids_igrejas, help='"🔍 Buscar Igreja"', placeholder='Digite a igreja.',format_func=lambda x: f'{x} - {next(i.nome for i in igrejas if i.id==x)}')
    usuarios = session.query(Usuarios).filter_by(igreja_id=igreja_selecionada).all()

else:
    usuarios = session.query(Usuarios).filter_by(igreja_id=st.session_state.igreja).all()

ids = [u.id for u in usuarios]
id_selecionado = st.selectbox('Usuário', ids, help='"🔍 Buscar Usuário"', placeholder='Digite o usuário.',format_func=lambda x: f'{x} - {next(p.nome for p in usuarios if p.id==x)}')
usuario = session.query(Usuarios).filter(Usuarios.id==id_selecionado).first()
# UI da página
st.title("📋 Editar Perfil")
if st.session_state['perfil'] == 'Supervisor':
    options = ['Supervisor','Administrador','Líder', 'Auxiliar']
else:
    options = ['Administrador','Líder', 'Auxiliar']

if usuario:
    with st.container(border=True):
        nome = st.text_input("Nome completo", disabled=True, value=usuario.nome)
        username = st.text_input("Usuário", disabled=True, value=usuario.cpf)

        # Corrigindo o index
        if usuario.perfil in options:
            perfil_index = options.index(usuario.perfil)
        else:
            perfil_index = 0  # valor padrão

        perfil = st.selectbox('Perfil', options=options, index=perfil_index)
        if perfil == 'Líder':
            ministerios_all = session.query(Ministerios).filter_by(igreja_id=st.session_state.igreja).all()
            usuario_selecionado = session.query(Usuarios).get(id_selecionado)
            ministerios = usuario_selecionado.ministerios
            ministerios_selecionados = st.multiselect(
                'Ministérios',
                options=[m.id for m in ministerios_all],
                default=[m.id for m in ministerios],
                format_func=lambda x: next(m.nome for m in ministerios_all if m.id == x)
            )
            telefone = st.text_input("Nº do telefone", placeholder='Apenas números! Ex. 81988887777',help='Não precisa colocar parênteses e nem traços ex: (81) 98888-7777', max_chars=11)


        enviar = st.button("Atualizar", key='warning')

        if enviar:
            try:
                if perfil in ['Líder', 'Administrador'] and not telefone:
                    st.warning('Para líderes e administradores é necessário nº de telefone')
                    st.stop()
                usuario.perfil = perfil
                usuario.ministerios = [session.query(Ministerios).get(mid) for mid in ministerios_selecionados]
                session.commit()
                st.success('Usuário atualizado com sucesso!')
            except Exception as e:
                session.rollback()
                st.error(f'Erro ao atualizar usuário: {e}')
            finally:
                session.close()
else:
    st.warning('Usuário não encontrado!')