import streamlit as st
from db import SessionLocal
from models import Ministerios
import time

st.set_page_config(layout='centered')
with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
session = SessionLocal()

st.title("✏️ Editar Grupo/Ministério")

# Buscar todos os grupos cadastrados
grupos = session.query(Ministerios).all()

if not grupos:
    st.warning("Nenhum grupo/ministério cadastrado ainda.")
else:
    # Selecionar grupo pelo objeto
    ids = [grupo.id for grupo in grupos]
    id_selecionado = st.selectbox(
        "Selecione o grupo/ministério para editar:",
        options=ids,
        format_func=lambda x: f"{x} - {next((p.nome for p in grupos if p.id == x), '')}"
    )

    grupo_selecionado = session.query(Ministerios).get(id_selecionado)

    with st.form("form_editar", clear_on_submit=True):
        novo_nome = st.text_input("Novo nome do grupo/ministério", value=grupo_selecionado.nome)
        with st.container(horizontal=True, vertical_alignment='bottom'):
            salvar = st.form_submit_button("Salvar alterações", key='primary')
            deletar = st.form_submit_button('Deletar', key='danger')

        if salvar:
            try:
                grupo_selecionado.nome = novo_nome.strip()
                session.commit()
                st.success("Grupo atualizado com sucesso!")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao atualizar grupo: {e}")
            finally:
                session.close()
        if deletar:
            # Diálogo de confirmação
            @st.dialog("Confirmação de exclusão")
            def confirmar_exclusao():
                st.write(f"Tem certeza que deseja excluir o grupo **{grupo_selecionado.nome}**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar exclusão"):
                        try:
                            session.delete(grupo_selecionado)
                            session.commit()
                            st.success(f"Grupo '{grupo_selecionado.nome}' excluído com sucesso!")
                            time.sleep(2)
                            st.rerun()  # recarrega a página
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro ao excluir grupo: {e}")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()


            confirmar_exclusao()
