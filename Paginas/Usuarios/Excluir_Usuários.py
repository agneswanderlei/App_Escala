import streamlit as st
from db import SessionLocal
from models import Usuarios, Igrejas
import time

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("🗑️ Excluir Usuário")

perfil_logado = st.session_state.get('perfil')
igreja_logada = st.session_state.get('igreja')

# ----- Buscar usuários conforme perfil -----
if perfil_logado == 'Supervisor':
    # Supervisor escolhe a igreja primeiro
    igrejas = session.query(Igrejas).all()
    ids_igrejas = [i.id for i in igrejas]

    igreja_selecionada = st.selectbox(
        "Selecione a Igreja",
        ids_igrejas,
        format_func=lambda x: f"{x} - {next(i.nome for i in igrejas if i.id == x)}"
    )

    usuarios = session.query(Usuarios).filter_by(igreja_id=igreja_selecionada).all()

elif perfil_logado == 'Administrador':
    # Administrador só vê usuários da própria igreja
    usuarios = session.query(Usuarios).filter_by(igreja_id=igreja_logada).all()

else:
    st.warning("⚠️ Você não tem permissão para excluir usuários.")
    usuarios = []

# ----- Exibir lista de usuários -----
if usuarios:
    ids = [u.id for u in usuarios]
    id_selecionado = st.selectbox(
        "Selecione o usuário para excluir:",
        ids,
        format_func=lambda x: f"{x} - {next(u.nome for u in usuarios if u.id == x)}"
    )

    usuario = session.query(Usuarios).filter(Usuarios.id == id_selecionado).first()

    if usuario:
        st.write(f"👤 Usuário selecionado: **{usuario.nome}** (CPF: {usuario.cpf})")

        if st.button("Excluir Usuário", type="primary"):
            try:
                session.delete(usuario)
                session.commit()
                st.success(f"Usuário '{usuario.nome}' excluído com sucesso! ✅")
                time.sleep(2)
                st.rerun()  # recarrega a página para atualizar lista
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao excluir usuário: {e}")
            finally:
                session.close()
else:
    if perfil_logado in ['Supervisor','Administrador']:
        st.info("Nenhum usuário disponível para exclusão.")