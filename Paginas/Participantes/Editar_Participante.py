import streamlit as st
from db import SessionLocal
from models import Participantes, Ministerios, Funcoes
import time
import os

st.set_page_config(layout='centered')
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

session = SessionLocal()

st.title("✏️ Editar Participante")

# Buscar todos os participantes cadastrados
igreja_id = st.session_state.igreja
perfil = st.session_state.perfil

if perfil == 'Supervisor':
    participantes = session.query(Participantes).all()
elif perfil == 'Administrador':
    participantes = session.query(Participantes).filter_by(igreja_id=igreja_id)

if not participantes:
    st.warning("Nenhum participante cadastrado ainda.")
else:
    ids = [p.id for p in participantes]
    id_selecionado = st.selectbox(
        "Selecione o participante para editar:",
        options=ids,
        format_func=lambda x: f"{x} - {next((p.nome for p in participantes if p.id == x), '')}"
    )

    participante_selecionado = session.query(Participantes).get(id_selecionado)

    # Buscar ministérios e funções da igreja
    ministerios = session.query(Ministerios).filter_by(igreja_id=participante_selecionado.igreja_id).all()
    funcoes = session.query(Funcoes).filter_by(igreja_id=participante_selecionado.igreja_id).all()

    # IDs já vinculados
    ministerios_ids = [m.id for m in participante_selecionado.ministerios]
    funcoes_ids = [f.id for f in participante_selecionado.funcoes]

    with st.form("form_editar"):
        novo_nome = st.text_input("Novo nome do participante", value=participante_selecionado.nome)
        telefone = st.text_input("Telefone", value=participante_selecionado.telefone)

        ministerios_escolhidos = st.multiselect(
            "Ministérios",
            options=[f"{m.id} - {m.nome}" for m in ministerios],
            default=[f"{m.id} - {m.nome}" for m in ministerios if m.id in ministerios_ids]
        )

        funcoes_escolhidas = st.multiselect(
            "Funções",
            options=[f"{f.id} - {f.nome}" for f in funcoes],
            default=[f"{f.id} - {f.nome}" for f in funcoes if f.id in funcoes_ids]
        )

        with st.container(horizontal=True, vertical_alignment='bottom'):
            salvar = st.form_submit_button("Salvar alterações", key="success")
            deletar = st.form_submit_button("Deletar", key="danger")

        if salvar:
            try:
                participante_selecionado.nome = novo_nome.strip()
                participante_selecionado.telefone = telefone.strip()

                # Atualizar ministérios
                participante_selecionado.ministerios.clear()
                for mid in ministerios_escolhidos:
                    m_id = int(mid.split(" - ")[0])
                    ministerio = session.query(Ministerios).get(m_id)
                    participante_selecionado.ministerios.append(ministerio)

                # Atualizar funções
                participante_selecionado.funcoes.clear()
                for fid in funcoes_escolhidas:
                    f_id = int(fid.split(" - ")[0])
                    funcao = session.query(Funcoes).get(f_id)
                    participante_selecionado.funcoes.append(funcao)

                session.commit()
                st.success("Participante atualizado com sucesso!")
                time.sleep(2)
                st.switch_page(os.path.join('Paginas','Participantes','Participantes.py'))
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao atualizar participante: {e}")
            finally:
                session.close()

        if deletar:
            @st.dialog("Confirmação de exclusão")
            def confirmar_exclusao():
                st.write(f"Tem certeza que deseja excluir o participante **{participante_selecionado.nome}**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar exclusão"):
                        try:
                            session.delete(participante_selecionado)
                            session.commit()
                            st.success(f"Participante '{participante_selecionado.nome}' excluído com sucesso!")
                            time.sleep(2)
                            st.switch_page(os.path.join('Paginas','Participantes','Participantes.py'))
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro ao excluir participante: {e}")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()

            confirmar_exclusao()