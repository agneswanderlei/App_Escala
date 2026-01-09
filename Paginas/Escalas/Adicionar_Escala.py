import streamlit as st
from db import SessionLocal
from models import Eventos, Ministerios, Participantes, Indisponibilidades, Escalas

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Cadastro de Escala")

perfil = st.session_state.perfil
igreja_id = st.session_state.igreja

if perfil == 'Supervisor':
    ministerios = session.query(Ministerios).all()
    eventos = session.query(Eventos).all()
    participantes = session.query(Participantes).all()
else:
    ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
    eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).all()
    participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()

eventos_id = [e.id for e in eventos]
ministerios_id = [m.id for m in ministerios]

# with st.form("form_cadastro", clear_on_submit=True):
with st.container(border=True):
    evento = st.selectbox(
        "Evento",
        options=[e.id for e in eventos],
        format_func=lambda x: next((f'{e.nome} - {e.data.strftime("%d/%m/%Y")} - {e.hora.strftime("%H:%M") if e.hora else "Não especificada"}' for e in eventos if e.id == x), "")
    )
    ministerio = st.selectbox(
        "Ministério",
        options=[m.id for m in ministerios],
        format_func=lambda x: next((m.nome for m in ministerios if m.id == x), "")
    )

    # 🔎 Buscar participantes do ministério selecionado
    ministerio_obj = session.query(Ministerios).get(ministerio)
    participantes_ministerio = ministerio_obj.participantes if ministerio_obj else []
    participante = st.multiselect(
        "Participante",
        options=[p.id for p in participantes_ministerio],
        format_func=lambda x: next((p.nome for p in participantes_ministerio if p.id == x), "")
    )
    for p_id in participante:
        escala = session.query(Escalas).filter_by(participante_id=p_id).filter_by(evento_id=evento).first()
        if escala:
            st.info(f"O participante {session.query(Participantes).get(p_id).nome} já possui escala cadastrada para este evento.")

    descricao = st.text_area("Descrição do evento (opcional)", height=200)

    salvar = st.button("Cadastrar", type="primary")

    if salvar:
        try:
            # Validações
            if not evento or not ministerio or not participante:
                st.warning("Por favor, preencha todos os campos obrigatórios.")
                st.stop()
            evento_obj = session.query(Eventos).get(evento)

            # Buscar indisponibilidades na mesma data
            indisponibilidades = session.query(Indisponibilidades).filter(
                Indisponibilidades.participante_id.in_(participante),
                Indisponibilidades.data == evento_obj.data
            ).all()

            # Verificar conflito de horário
            conflitos = []
            for ind in indisponibilidades:
                # Se o evento tem hora definida
                if evento_obj.hora:
                    # Se a hora do evento está dentro do intervalo de indisponibilidade
                    if ind.hora_inicio and ind.hora_fim:
                        if ind.hora_inicio <= evento_obj.hora <= ind.hora_fim:
                            conflitos.append(ind.participante_id)
                    # Caso só tenha hora_inicio (indisponível a partir dali)
                    elif ind.hora_inicio and not ind.hora_fim:
                        if evento_obj.hora >= ind.hora_inicio:
                            conflitos.append(ind.participante_id)
                    # Caso só tenha hora_fim (indisponível até ali)
                    elif ind.hora_fim and not ind.hora_inicio:
                        if evento_obj.hora <= ind.hora_fim:
                            conflitos.append(ind.participante_id)

            if conflitos:
                nomes_indisponiveis = ', '.join([session.query(Participantes).get(pid).nome for pid in conflitos])
                st.error(f"Os seguintes participantes estão indisponíveis no horário do evento: {nomes_indisponiveis}")
                st.stop()
            # Aqui você deve salvar na tabela Escalas
            for p_id in participante:
                nova_escala = Escalas(
                    evento_id=evento,
                    ministerio_id=ministerio,
                    participante_id=p_id,
                    descricao=descricao
                )
                session.add(nova_escala)

            session.commit()
            st.success("Escala cadastrada com sucesso!")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao cadastrar Escala: {e}")
        finally:
            session.close()