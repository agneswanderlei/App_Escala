import streamlit as st
from db import SessionLocal
from models import Participantes, Indisponibilidades
import time, os

st.set_page_config(layout='centered', initial_sidebar_state='collapsed')
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

session = SessionLocal()

st.title("✏️ Editar Indisponibilidade")

# Buscar todos os participantes cadastrados
perfil = st.session_state.get("perfil")
igreja_id = st.session_state.get("igreja")
if perfil == 'Supervisor':
    participantes = session.query(Participantes).all()
elif perfil == "Administrador":
    participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()
else:
    participantes = session.query(Participantes).filter_by(usuario_id=st.session_state.get('user_id')).all()

if not participantes:
    st.warning("Nenhum participante cadastrado ainda.")
else:
    ids = [p.id for p in participantes]
    id_selecionado = st.selectbox(
        "Selecione o participante para editar:",
        options=ids,
        format_func=lambda x: f"{x} - {next((p.nome for p in participantes if p.id == x), '')}"
    )

    indisponibilidade = session.query(Indisponibilidades).filter_by(participante_id=id_selecionado)
    ids_ind = [i.id for i in indisponibilidade]
    id_selecionado_ind = st.selectbox(
        'Selecione a indisponibilidade',
        options=ids_ind,
        # format_func=lambda x: f"{x} - {next((i.data.strftime('%d/%m/%Y') for i in indisponibilidade if i.id == x), '')}"
        format_func=lambda x: next(f"{i.data.strftime('%d/%m/%Y')} - {i.hora_inicio.strftime('%H:%M')}" for i in indisponibilidade if i.id == x)
    )
    ind_selecionada = session.query(Indisponibilidades).get(id_selecionado_ind)
    if ind_selecionada:
        with st.form("form_indisponibilidade", clear_on_submit=True):
            with st.container(horizontal=True, vertical_alignment='bottom'):
                data = st.date_input('Data', value=ind_selecionada.data, format='DD/MM/YYYY')
                hora_inicio = st.time_input('Hora Inicial', value=ind_selecionada.hora_inicio)
                hora_fim = st.time_input('Hora Final', value=ind_selecionada.hora_fim)
            motivo = st.text_area('Motivo', value=ind_selecionada.motivo)
            with st.container(horizontal=True, vertical_alignment='bottom'):
                salvar = st.form_submit_button("Salvar alterações", key="success")
                deletar = st.form_submit_button("Deletar", key="danger")
            if salvar:
                if hora_inicio and hora_fim:
                    if hora_fim < hora_inicio:
                        st.warning('A hora final deve ser maior que a inicial')
                        st.stop()
                try:
                    ind_selecionada.data = data
                    ind_selecionada.hora_inicio = hora_inicio
                    ind_selecionada.hora_fim = hora_fim
                    ind_selecionada.motivo = motivo
                    session.commit()
                    st.success("Indisponibilidade atualizada com sucesso!")
                    time.sleep(2)
                    st.switch_page(os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'))
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro ao atualizar Indisponibilidade: {e}")
                finally:
                    session.close()

            if deletar:
                @st.dialog("Confirmação de exclusão")
                def confirmar_exclusao():

                    st.write(f"Tem certeza que deseja excluir a Indisponibilidade.")
                    st.write(f"Motivo: **{ind_selecionada.motivo}**")
                    st.write(f"Data: **{ind_selecionada.data.strftime('%d/%m/%Y')}**")
                    st.write(f"Hora inicial: **{ind_selecionada.hora_inicio.strftime('%H:%M')}**")
                    st.write(f"Hora final: **{ind_selecionada.hora_fim.strftime('%H:%M')}**")
                    
                    with st.container(horizontal=True, vertical_alignment='bottom'):
                        if st.button("✅ Confirmar exclusão"):
                            try:
                                session.delete(ind_selecionada)
                                session.commit()
                                st.success(f"Indisponibilidade '{ind_selecionada.data.strftime('%d/%m/%Y')}' excluída com sucesso!")
                                time.sleep(2)
                                st.switch_page(os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'))
                            except Exception as e:
                                session.rollback()
                                st.error(f"Erro ao excluir participante: {e}")
                    
                        if st.button("❌ Cancelar"):
                            st.rerun()

                confirmar_exclusao()
    else:
        st.info('O Participante não possui nenhuma indisponibilidade cadastrada!')           