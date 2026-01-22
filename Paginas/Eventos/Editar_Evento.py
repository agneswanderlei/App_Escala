import streamlit as st
from db import SessionLocal
from models import Eventos
import time

st.set_page_config(layout='centered')
session = SessionLocal()
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("📋 Editar de Eventos")
if 'evento' not in st.session_state:
    st.session_state.evento = None

perfil = st.session_state.perfil
igreja_id = st.session_state.igreja

if perfil == 'Supervisor':
    st.session_state.evento = session.query(Eventos).all()
else:
    st.session_state.evento = session.query(Eventos).filter_by(igreja_id=igreja_id).all()

if not st.session_state.evento:
    st.warning("Nenhum evento encontrado.")
    st.stop()
id_evento = [e.id for e in st.session_state.evento]
evento_selecionado = st.selectbox("Selecione o evento para editar:", options=id_evento, format_func=lambda x: f"{x} - {next(e.nome for e in st.session_state.evento if e.id == x)}")
eventos = next(e for e in st.session_state.evento if e.id == evento_selecionado)

with st.form("form_cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do evento", value=eventos.nome)
    with st.container(horizontal=True):
        data = st.date_input("Data do evento", format="DD/MM/YYYY", value=eventos.data)
        hora = st.time_input("Hora do evento", value=eventos.hora, step=300)
    descricao = st.text_area("Descrição do evento (opcional)", height=200, value=eventos.descricao)
    with st.container(horizontal=True, vertical_alignment='bottom'):
        salvar = st.form_submit_button("Salvar", key="primary")
        deletar = st.form_submit_button("Deletar", key="danger")
    if salvar:
        try:
            eventos.nome = nome
            eventos.data = data
            eventos.hora = hora
            eventos.descricao = descricao

            session.commit()

            st.success(f"Evento '{eventos.nome}' atualizado com sucesso!")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao atualizar Evento: {e}")
        finally:
            session.close()
    if deletar:
        @st.dialog("Confirmação de exclusão")
        def confirmar_exclusao():
            st.write(f"Tem certeza que deseja excluir o evento:")
            st.write(f"nome: **{eventos.nome}**")
            st.write(f"Data: **{eventos.data.strftime('%d/%m/%Y')}**")
            st.write(f"Hora: **{eventos.hora.strftime('%H:%M')}**")
            col1, col2 = st.columns(2)
            with st.container(horizontal=True):
                if st.button("✅ Confirmar exclusão"):
                    try:
                        session.delete(eventos)
                        session.commit()
                        st.success(f"Evento '{eventos.nome}' excluído com sucesso!")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        session.rollback()
                        st.error(f"Erro ao excluir evento: {e}")
                    finally:
                        session.close()
                if st.button("❌ Cancelar"):
                    st.rerun()

        confirmar_exclusao()
       