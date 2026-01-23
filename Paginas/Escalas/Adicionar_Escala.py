import streamlit as st
from db import SessionLocal
from models import Eventos, Ministerios, Participantes, Indisponibilidades, Escalas, participante_funcao, Funcoes, DescricaoEscala, Igrejas, Usuarios
import pandas as pd
from Paginas.Escalas.jobs import enviar_lembrete
from Paginas.Escalas.Enviar_mensagens import send_whatsapp_message
# --- Adicionando o diretório pai ao path de busca ---
import sys
import os
print("PATH:", sys.path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
st.set_page_config(layout='centered')
with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



session = SessionLocal()
if 'lista_participante_funcao' not in st.session_state:
    st.session_state.lista_participante_funcao = {}
scheduler = st.session_state.scheduler
st.title("📋 Cadastro de Escala")

perfil = st.session_state.perfil
igreja_id = st.session_state.igreja

if perfil == 'Supervisor':
    ministerios = session.query(Ministerios).all()
    eventos = session.query(Eventos).all()
    participantes = session.query(Participantes).all()
if perfil == 'Administrador':
    ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
    eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).all()
    participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()
if perfil == 'Líder':
    usuario_logado = session.query(Usuarios).get(st.session_state.user_id)
    ministerios = usuario_logado.ministerios
    eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).all()
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
    with st.container(horizontal=True, vertical_alignment='bottom'):
        participante = st.selectbox(
            "Participante",
            options=[p.id for p in participantes_ministerio],
            format_func=lambda x: next((p.nome for p in participantes_ministerio if p.id == x), "")
        )
        funcao_participante = session.query(participante_funcao).filter_by(participante_id=participante).all()
        funcao = st.selectbox(
            "Função",
            options=[f.funcao_id for f in funcao_participante],
            format_func=lambda x: session.query(Funcoes).get(x).nome if session.query(Funcoes).get(x) else ""
        )
        add_participante = st.button('Adicionar', key='success')
        if add_participante:
            st.session_state.lista_participante_funcao[participante] = (funcao, ministerio)
        del_participante = st.button('Retirar', key='danger')
        if del_participante:
            del st.session_state.lista_participante_funcao[participante]
    # Tabela participantes com funcao:
    dados_convertidos = [
        {
            'Participante': session.query(Participantes).get(p_id).nome,
            'Função': session.query(Funcoes).get(f_id).nome if f_id else ""
        }
        for p_id,(f_id,_) in st.session_state.lista_participante_funcao.items()
    ]
    dados = pd.DataFrame(
        dados_convertidos,
        columns=['Participante', 'Função']
    )
    escala = session.query(Escalas).filter_by(participante_id=participante).filter_by(evento_id=evento).first()
    if escala:
        st.info(f"O participante {session.query(Participantes).get(participante).nome} já possui escala cadastrada para este evento.")
    st.dataframe(
        dados,
        width='stretch'
    )

    descricao = st.text_area("Descrição da escala (opcional)", height=200)

    salvar = st.button("Cadastrar", key="primary")
    # Instancia
    instancia =session.query(Igrejas).get(igreja_id).instancia
    
    if salvar:
        try:
            # Validações
            if not evento or not ministerio or not participante:
                st.warning("Por favor, preencha todos os campos obrigatórios.")
                st.stop()
            evento_obj = session.query(Eventos).get(evento)

            # Buscar indisponibilidades na mesma data

            indisponibilidades = session.query(Indisponibilidades).filter(
                Indisponibilidades.participante_id.in_(list(st.session_state.lista_participante_funcao.keys())),
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
            for p_id, (f_id,m_id) in st.session_state.lista_participante_funcao.items():
                ministerio_add = session.query(Escalas).filter_by(ministerio_id=m_id,igreja_id=igreja_id, evento_id=evento).first()
                if ministerio_add:
                    st.warning(f'O ministerio {ministerio_add.ministerio.nome} já foi cadastrado para o evento {ministerio_add.evento.nome}!')
                    st.stop()
                nova_escala = Escalas(
                    evento_id=evento,
                    ministerio_id=m_id,
                    participante_id=p_id,
                    funcao_id=f_id,
                    igreja_id=igreja_id,

                )
                session.add(nova_escala)
                # Textos
                nome = session.query(Participantes).get(p_id).nome.upper()
                evento_obj = session.query(Eventos).get(evento)
                evento_nome = evento_obj.nome
                evento_data = evento_obj.data.strftime('%d/%m/%Y')
                evento_hora = evento_obj.hora.strftime('%H:%M') if evento_obj.hora else "Não especificada"
                ministerio_nome = session.query(Ministerios).get(ministerio).nome.upper()
                funcao_nome = session.query(Funcoes).get(f_id).nome
                igreja_nome = session.query(Igrejas).get(igreja_id).nome.upper()

                responsavel_telefone = st.session_state.telefone

                link_responsavel = f"https://api.whatsapp.com/send?phone={responsavel_telefone}"

                texto = (
                    f"📣 Olá {nome}!\n\n"
                    f"Você foi escalado para o evento abaixo 🎉\n\n"
                    f"🏛️ *Igreja:* {igreja_nome}\n"
                    f"🗓️ *Evento:* {evento_nome}\n"
                    f"📅 *Data:* {evento_data}\n"
                    f"⏰ *Horário:* {evento_hora}\n"
                    f"🙌 *Ministério:* {ministerio_nome}\n"
                    f"👤 *Função:* {funcao_nome}\n\n"
                    f"⚠️ Caso não possa comparecer, fale diretamente com o responsável clicando no link abaixo:\n"
                    f"{link_responsavel}\n\n"
                    f"Qualquer dúvida, estamos à disposição 🙏\n"
                    f"Equipe {igreja_nome}"
                )
                resp = send_whatsapp_message(
                    number='55'+ session.query(Participantes).get(p_id).telefone,
                    text=texto,
                    instance_name=instancia
                )
                
                from datetime import datetime, timedelta

                evento_datetime = datetime.combine(evento_obj.data, evento_obj.hora)

                # 2 dias antes
                scheduler.add_job(
                    enviar_lembrete,
                    'date',
                    run_date=evento_datetime - timedelta(minutes=1),
                    args=[p_id, evento_obj.id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "2dias", instancia]
                )

                # 1 dia antes
                scheduler.add_job(
                    enviar_lembrete,
                    'date',
                    run_date=evento_datetime - timedelta(minutes=2),
                    args=[p_id, evento_obj.id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "1dia", instancia]
                )

                # 2 horas antes
                scheduler.add_job(
                    enviar_lembrete,
                    'date',
                    run_date=evento_datetime - timedelta(minutes=3),
                    args=[p_id, evento_obj.id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "2horas", instancia]
                )

            session.commit()
            nova_desc = DescricaoEscala(
                evento_id=evento,
                ministerio_id=ministerio,
                igreja_id=igreja_id,
                descricao=descricao,
            )

            session.add(nova_desc)
            session.commit()
            st.success("Escala cadastrada com sucesso!")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao cadastrar Escala: {e}")
        finally:
            session.close()