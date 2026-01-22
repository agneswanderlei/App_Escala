import streamlit as st
from db import SessionLocal
from models import Igrejas
import time

st.set_page_config(layout='centered')
with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
session = SessionLocal()

st.title("✏️ Editar Igreja")

# Buscar todas as igrejas cadastradas
igrejas = session.query(Igrejas).all()

if not igrejas:
    st.warning("Nenhuma igreja cadastrada ainda.")
else:
    # Selecionar igreja pelo objeto
    ids = [igreja.id for igreja in igrejas]
    id_selecionado = st.selectbox(
        "Selecione a igreja para editar:",
        options=ids,
        format_func=lambda x: f"{x} - {next((p.nome for p in igrejas if p.id == x), '')}"
    )

    igreja_selecionada = session.query(Igrejas).get(id_selecionado)

    with st.form("form_editar"):
        novo_nome = st.text_input("Novo nome da igreja", value=igreja_selecionada.nome)
        instancia = st.text_input("Nome da Instância")

        with st.container(horizontal=True, vertical_alignment='bottom'):
            salvar = st.form_submit_button("Salvar alterações", key='primary')
            deletar = st.form_submit_button('Deletar', key='danger')

        if salvar:
            try:
                igreja_selecionada.nome = novo_nome.strip()
                igreja_selecionada.instancia = instancia.strip()

                session.commit()
                st.success(f"Igreja atualizada para '{novo_nome}' com sucesso!")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao atualizar igreja: {e}")
            finally:
                session.close()
        if deletar:
            # Diálogo de confirmação
            @st.dialog("Confirmação de exclusão")
            def confirmar_exclusao():
                st.write(f"Tem certeza que deseja excluir a igreja **{igreja_selecionada.nome}**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar exclusão"):
                        try:
                            session.delete(igreja_selecionada)
                            session.commit()
                            st.success(f"Igreja '{igreja_selecionada.nome}' excluída com sucesso!")
                            time.sleep(2)
                            st.rerun()  # recarrega a página
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro ao excluir igreja: {e}")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.info("Exclusão cancelada.")

            confirmar_exclusao()
