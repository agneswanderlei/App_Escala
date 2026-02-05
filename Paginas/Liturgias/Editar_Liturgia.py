import streamlit as st
from db import SessionLocal
from models import Eventos, Participantes, Liturgias, MomentosLiturgia
import datetime

st.set_page_config(layout='centered')
session = SessionLocal()
if 'momentos_state_edite' not in st.session_state:
    st.session_state.momentos_state_edite = {}
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
def carregar_momentos():
    momento_id = st.session_state["liturgia_select2"]
    momentos_db = session.query(MomentosLiturgia).filter_by(
        liturgia_id=momento_id
    ).all()
    st.session_state.momentos_state_edite = {}
    for m in momentos_db:
        hora = m.horario
        desc = m.descricao
        resp = [m.responsavel_id] if m.responsavel_id else []
        st.session_state.momentos_state_edite[hora] = (desc, resp)

st.title("📋 Editar Liturgia")

igreja_id = st.session_state.igreja

# Buscar eventos e participantes
eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).order_by(Eventos.data.asc())
participantes = session.query(Participantes).filter_by(igreja_id=igreja_id)

ids_evento = [e.id for e in eventos]
evento_id = st.selectbox(
    'Evento',
    options=ids_evento,
    format_func=lambda x: next(f"{e.data.strftime('%d/%m/%Y')} - {e.nome}" for e in eventos if e.id == x)
)

# Buscar liturgias existentes para o evento selecionado
liturgias = session.query(Liturgias).filter_by(evento_id=evento_id).all()
ids_liturgia = [l.id for l in liturgias]

liturgia_id = st.selectbox(
    "Liturgia",
    options=ids_liturgia,
    key='liturgia_select2',
    on_change=carregar_momentos,
    format_func=lambda x: next(l.nome for l in liturgias if l.id == x)
) if ids_liturgia else None

# Carregar liturgia selecionada
liturgia = session.query(Liturgias).get(liturgia_id) if liturgia_id else None

ids_participante = [p.id for p in participantes]

# Sempre que mudar a liturgia, recarregar momentos_state_edite
if liturgia and not st.session_state.momentos_state_edite:
    # Só carrega do banco se ainda não tiver nada no session_state
    for m in liturgia.momentos:
        hora = m.horario
        desc = m.descricao
        resp = [m.responsavel_id] if m.responsavel_id else []
        st.session_state.momentos_state_edite[hora] = (desc, resp)

if liturgia:

    with st.container(border=True):
        nome = st.text_input('Nome da liturgia', value=liturgia.nome if liturgia else "")

        with st.container(horizontal=True, vertical_alignment='bottom', gap='small', horizontal_alignment='center'):
            col1, col2, col3 = st.columns([1.2, 2, 2])
            with col1:
                hora = st.time_input('hora', step=60, value=None)
            with col2:
                descricao = st.text_input('Descrição')
            with col3:
                responsaveis = st.multiselect(
                    'Responsáveis',
                    options=ids_participante,
                    format_func=lambda x: next(p.nome for p in participantes if p.id == x)
                )
            add = st.button('Add', key='success')
            deletar = st.button('Del', key='danger')

        if add and responsaveis:
            st.session_state.momentos_state_edite[hora] = (descricao, responsaveis)
        if deletar and hora in st.session_state.momentos_state_edite:
            del st.session_state.momentos_state_edite[hora]

        # Mostrar tabela sempre com os momentos atuais
        dados = [{
            "Hora": h.strftime("%H:%M"),
            "Descrição": desc,
            "Responsáveis": ", ".join(
                next((p.nome for p in participantes if p.id == pid), "-")
                for pid in resp
            ) if resp else "-"
        } for h, (desc, resp) in sorted(st.session_state.momentos_state_edite.items())]

        st.dataframe(dados)
        descricao_liturgia = st.text_area('Descrição Liturgia', value=session.query(Liturgias).get(liturgia_id).descricao)
        with st.container(horizontal=True):

            salvar = st.button('Salvar', key='primary')
            excluir = st.button('Excluir liturgia', type='primary')
        if salvar and liturgia:
            # Atualizar nome
            liturgia.nome = nome
            liturgia.descricao = descricao_liturgia
            # Apagar momentos antigos
            session.query(MomentosLiturgia).filter_by(liturgia_id=liturgia.id).delete()

            # Inserir momentos novos
            for hora, (desc, responsaveis) in st.session_state.momentos_state_edite.items():
                for pid in responsaveis:
                    momento = MomentosLiturgia(
                        horario=hora,
                        descricao=desc,
                        responsavel_id=pid,
                        liturgia_id=liturgia.id
                    )
                    session.add(momento)

            session.commit()
            st.success("Liturgia atualizada com sucesso!")
        if excluir:
            @st.dialog('Confirmação')
            def msg_deletar():
                st.write(f'Deseja mesmo excluir **{session.query(Liturgias).get(liturgia_id).nome}**?')
                
                with st.container(horizontal=True):
                    confirmar = st.button('Confirmar')
                    cancelar = st.button('Cancelar')
                if confirmar:
                    session.query(MomentosLiturgia).filter_by(
                        liturgia_id=liturgia_id
                    ).delete()
                    session.commit()
                    session.query(Liturgias).filter_by(id=liturgia_id).delete()
                    session.commit()
                    st.toast('Liturgia excluída com sucesso!', icon='✅')
                if cancelar:
                    st.rerun()
            msg_deletar()
else:
    st.info('Não existe liturgia cadastrada para esse evento.')