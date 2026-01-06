import streamlit as st
from db import SessionLocal
from models import Participantes, Indisponibilidades, Igrejas
import datetime

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📅 Cadastro de Indisponibilidades")

perfil = st.session_state.get("perfil")
igreja_id = st.session_state.get("igreja")

# ----- Buscar participantes conforme perfil -----
if perfil == "Supervisor":
    participantes = session.query(Participantes).all()
elif perfil == "Administrador":
    participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()
else:  # Líder ou Auxiliar
    participantes = session.query(Participantes).filter_by(usuario_id=st.session_state.get("user_id")).all()

if not participantes:
    st.warning("Nenhum participante cadastrado ainda.")
else:
    opcoes_participantes = [f"{p.id} - {p.nome}" for p in participantes]

    with st.form("form_indisponibilidade", clear_on_submit=True):
        if perfil in ["Supervisor", "Administrador"]:
            escolha = st.selectbox("Selecione o participante:", options=opcoes_participantes, index=None)
        else:
            participante_logado = participantes[0]  # só existe o próprio
            escolha = f"{participante_logado.id} - {participante_logado.nome}"
            st.markdown(f"**Participante:** {participante_logado.nome}")

        data = st.date_input("Data da indisponibilidade", value=datetime.date.today(), format="DD/MM/YYYY")
        hora_inicio = st.time_input("Hora início", value=None)
        hora_fim = st.time_input("Hora fim", value=None)
        motivo = st.text_area("Motivo", placeholder="Ex: viagem, trabalho, saúde...")

        salvar = st.form_submit_button("Cadastrar", type="primary")

        if salvar:
            try:
                participante_id = int(escolha.split(" - ")[0])

                nova_indisponibilidade = Indisponibilidades(
                    participante_id=participante_id,
                    data=data,
                    hora_inicio=hora_inicio if hora_inicio else None,
                    hora_fim=hora_fim if hora_fim else None,
                    motivo=motivo.strip() if motivo else None
                )

                session.add(nova_indisponibilidade)
                session.commit()

                st.success(f"Indisponibilidade cadastrada para {escolha} em {data.strftime('%d/%m/%Y')}")
            except Exception as e:
                session.rollback()
                st.error(f"Erro ao cadastrar indisponibilidade: {e}")
            finally:
                session.close()