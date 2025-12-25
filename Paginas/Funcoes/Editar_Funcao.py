import streamlit as st
from db import SessionLocal
from models import Funcoes
import time

st.set_page_config(layout='centered')
with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
session = SessionLocal()

st.title("✏️ Editar Igreja")

# Buscar todas as igrejas cadastradas
funcoes = session.query(Funcoes).all()

if not funcoes:
    st.warning("Nenhuma função cadastrada ainda.")
else:
    # Selecionar igreja pelo objeto
    ids = [funcao.id for funcao in funcoes]
    id_selecionado = st.selectbox(
        "Selecione a função para editar:",
        options=ids,
        format_func=lambda x: f"{x} - {next((p.nome for p in funcoes if p.id == x), '')}"
    )

    funcao_selecionada = session.query(Funcoes).get(id_selecionado)

    with st.form("form_editar"):
        novo_nome = st.text_input("Novo nome da função", value=funcao_selecionada.nome)
        novo_descricao = st.text_area('Nova descrição', value=funcao_selecionada.descricao)
        with st.container(horizontal=True, vertical_alignment='bottom'):
            salvar = st.form_submit_button("Salvar alterações", key='primary')
            deletar = st.form_submit_button('Deletar', key='danger')

        if salvar:
            try:
                funcao_selecionada.nome = novo_nome.strip()
                funcao_selecionada.descricao = novo_descricao
                session.commit()
                st.success("Função atualizada com sucesso!")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao atualizar função: {e}")
            finally:
                session.close()
        if deletar:
            # Diálogo de confirmação
            @st.dialog("Confirmação de exclusão")
            def confirmar_exclusao():
                st.write(f"Tem certeza que deseja excluir a funcao **{funcao_selecionada.nome}**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar exclusão"):
                        try:
                            session.delete(funcao_selecionada)
                            session.commit()
                            st.success(f"Função '{funcao_selecionada.nome}' excluída com sucesso!")
                            time.sleep(2)
                            st.rerun()  # recarrega a página
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro ao excluir função: {e}")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()


            confirmar_exclusao()
