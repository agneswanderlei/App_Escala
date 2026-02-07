import streamlit as st
from db import SessionLocal
from models import Eventos, Ministerios, Participantes, Escalas, Funcoes, participante_funcao, Indisponibilidades, DescricaoEscala, Igrejas
import pandas as pd
import requests
from dotenv import load_dotenv
import os, time
from pathlib import Path
# CRIAR NOVOS JOBS PARA ESTE PARTICIPANTE
from datetime import datetime, timedelta
from Paginas.Escalas.jobs import enviar_lembrete

# Força o caminho absoluto para o .env na raiz
env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(env_path)
EVOLUTION_AUTHENTICATION_API_KEY = os.getenv('AUTHENTICATION_API_KEY')

st.set_page_config(layout='centered')
with open('Paginas/Usuarios/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def send_whatsapp_message(number: str, text: str, instance_name: str):
    """
    Envia uma mensagem de texto via WhatsApp.
    O nome da instância é passado dinamicamente.
    """
    url = f'http://72.60.155.96:8080/message/sendText/{instance_name}'
    headers = {
        'apikey': EVOLUTION_AUTHENTICATION_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'number': number,
        'text': text,
    }
    response = requests.post(
        url=url,
        json=payload,
        headers=headers
    )
    return response.json()
session = SessionLocal()
def carregar_escalas():
    evento_id = st.session_state["evento_select"]  # pega o valor do selectbox
    if evento_id:
        escalas_db = session.query(Escalas).filter_by(
            igreja_id=igreja_id, evento_id=evento_id
        ).all()
        st.session_state.lista_participante_escala_funcao = [
            (esc.participante_id, esc.funcao_id, esc.ministerio_id)
            for esc in escalas_db
        ]

st.title("📋 Editar Escalas")

igreja_id = st.session_state.igreja
if 'lista_participante_escala_funcao' not in st.session_state:
    st.session_state.lista_participante_escala_funcao = []
# Buscar dados da igreja
ministerios = session.query(Ministerios).filter_by(igreja_id=igreja_id).all()
eventos = session.query(Eventos).filter_by(igreja_id=igreja_id).all()
funcoes = session.query(Funcoes).filter_by(igreja_id=igreja_id).all()
participantes = session.query(Participantes).filter_by(igreja_id=igreja_id).all()

with st.container(border=True):
    # Selectbox de evento e ministério
    with st.container(horizontal=True, vertical_alignment='bottom'):
        evento = st.selectbox(
            'Eventos',
            options=[e.id for e in eventos],
            format_func=lambda x: next(f"{e.nome} - {e.data.strftime('%d/%m/%Y')} - {e.hora.strftime('%H:%M')}" for e in eventos if e.id == x),
            index=None,
            key='evento_select',
            on_change=carregar_escalas

        )
        ministerio = st.selectbox(
            'Ministérios',
            options=[m.id for m in ministerios],
            format_func= lambda x: next(m.nome for m in ministerios if m.id == x),
            index=None
        )

    # Inicializar state com escalas do evento
    if not evento:
        
        st.info('Selecione um evento.')
    
    ## Seleção de participante e função
    # Seleção de participante
    with st.container(horizontal=True, vertical_alignment='bottom'):
        participante = st.selectbox(
            'Participantes',
            options= [p.id for p in participantes],
            format_func= lambda x: next(p.nome for p in participantes if p.id == x),
            index=None
        )
        funcao_db = []
        if participante:
            funcao_db = session.query(participante_funcao).filter_by(participante_id=participante).all()
        funcao = st.selectbox(
            'Função',
            options=[f.funcao_id for f in funcao_db],
            format_func=lambda x: next(f.nome for f in funcoes if f.id == x)
        )
        add = st.button('Adicionar', key='primary')
        if add:
            lista_participantes= []
            for p_id, f_id, m_id in st.session_state.lista_participante_escala_funcao:
                lista_participantes.append(p_id)
                
            if participante  not in lista_participantes and ministerio:
                st.session_state.lista_participante_escala_funcao.append(
                    (participante,funcao,ministerio)
                )
            elif participante  not in lista_participantes and not ministerio:
                st.toast('Selecione o ministerio',icon='⚠️')
            else:
                st.toast('Participante já adicionado na lista abaixo.', icon='⚠️')
        retirar = st.button('Retirar', key='warning')
        if retirar:
            try:
                st.session_state.lista_participante_escala_funcao.remove((participante, funcao, ministerio))
            except ValueError:
                st.toast('Os campos ministérios, participantes e função devem tá preenchidos.', icon='⚠️')


    # Verificar impedimentos e duplicidade
    conflitos = 0
    evento_obj = session.query(Eventos).get(evento)
    if participante and evento:
        # 1. Verificar indisponibilidade considerando intervalo de horas
        indisponibilidades = session.query(Indisponibilidades).filter_by(
            participante_id = participante,
            igreja_id = igreja_id,
            data = evento_obj.data
        ).all()
        for ind in indisponibilidades:
            if ind.hora_inicio and ind.hora_fim and evento_obj.hora:
                if ind.hora_inicio <= evento_obj.hora <= ind.hora_fim:
                    st.warning(
                        f"⚠️ O participante está indisponível em "
                        f"{evento_obj.data.strftime('%d/%m/%Y')}"
                        f" das {ind.hora_inicio.strftime('%H:%M')} as {ind.hora_fim.strftime('%H:%M')}"
                    )
            elif evento_obj.hora is None:
                st.warning(
                    f"⚠️ O participante está indisponível em "
                    f"{evento_obj.data.strftime('%d/%m/%Y')}"
                )
        # 2. Verificar se já está escalado
        # Preciso ver no banco se o participante já está escalado no evento
        ja_escalado = session.query(Escalas).filter_by(
            igreja_id=igreja_id,
            evento_id=evento,
            participante_id=participante
        ).first()
        if ja_escalado:
            st.info(f'Participante já escalado no ministério {ja_escalado.ministerio.nome}!')
    # dados tabela
    dados_convertidos = [
        {
            'Participantes': session.query(Participantes).get(p_id).nome,
            'Funções': session.query(Funcoes).get(f_id).nome if f_id else "",
            'Ministérios': session.query(Ministerios).get(m_id).nome if m_id else ""
            
        }
        for (p_id, f_id, m_id) in st.session_state.lista_participante_escala_funcao if ministerio is None or m_id == ministerio
    ]
    dados = pd.DataFrame(
        dados_convertidos,
        columns=['Participantes', 'Funções', 'Ministérios']
    )
    st.dataframe(
        dados,
        width='stretch'
    )
    
    desc=session.query(DescricaoEscala).filter_by(
            igreja_id=igreja_id,
            evento_id=evento,
            ministerio_id=ministerio
        ).first()
    descricao = st.text_area(
        'Descrição',
        height=200,
        value=desc.descricao if desc else None
    )
    with st.container(horizontal=True):
        escala_evento = session.query(Escalas).filter_by(
            igreja_id=igreja_id,
            evento_id=evento
        ).all()
        if evento:
            indisp = session.query(Indisponibilidades).filter_by(
                igreja_id=igreja_id,
                data=evento_obj.data
            )

        atualizar = st.button('Atualizar', key='success')
        if atualizar:
            # Instancia
            instancia = session.query(Igrejas).get(igreja_id).instancia
            scheduler = st.session_state.scheduler
            
            try:
                # 1. PEGAR PARTICIPANTES ANTIGOS DESTE MINISTÉRIO NO EVENTO
                escalas_antigas = session.query(Escalas).filter_by(
                    igreja_id=igreja_id,
                    evento_id=evento,
                    ministerio_id=ministerio  # ← FILTRAR APENAS ESTE MINISTÉRIO
                ).all()
                
                # Pegar IDs dos participantes antigos
                participantes_antigos_ids = [esc.participante_id for esc in escalas_antigas]
                
                # 2. REMOVER JOBS APENAS DOS PARTICIPANTES DESTE MINISTÉRIO
                jobs_existentes = scheduler.get_jobs()
                for job in jobs_existentes:
                    # Verificar se o job é relacionado a este evento E a um participante deste ministério
                    # job.args = [p_id, evento_id, ministerio_nome, funcao_nome, igreja_nome, link, tipo, instancia]
                    if (len(job.args) > 1 and 
                        job.args[1] == evento and  # mesmo evento
                        job.args[0] in participantes_antigos_ids):  # participante do ministério sendo editado
                        scheduler.remove_job(job.id)
                
                # 3. Apagar escalas antigas APENAS DESTE MINISTÉRIO
                session.query(Escalas).filter_by(
                    igreja_id=igreja_id,
                    evento_id=evento,
                    ministerio_id=ministerio  # ← FILTRAR APENAS ESTE MINISTÉRIO
                ).delete()

                # 4. Recriar escalas a partir do state (APENAS DO MINISTÉRIO SELECIONADO)
                for (p_id, f_id, m_id) in st.session_state.lista_participante_escala_funcao:
                    # Só processar se for do ministério sendo editado
                    if m_id != ministerio:
                        continue
                        
                    # Verificar indisponibilidade
                    indisp = session.query(Indisponibilidades).filter_by(
                        igreja_id=igreja_id,
                        participante_id=p_id,
                        data=evento_obj.data
                    )
                    conflito = False
                    for ind in indisp:
                        if ind.hora_inicio and ind.hora_fim and evento_obj.hora:
                            if ind.hora_inicio <= evento_obj.hora <= ind.hora_fim:
                                st.toast(
                                    f"⚠️ O participante {session.query(Participantes).get(p_id).nome} "
                                    f"está indisponível em {evento_obj.data.strftime('%d/%m/%Y')} "
                                    f"das {ind.hora_inicio.strftime('%H:%M')} às {ind.hora_fim.strftime('%H:%M')}",
                                    icon='⚠️'
                                )
                                conflito = True
                    if conflito:
                        continue
                        
                    nova = Escalas(
                        evento_id=evento,
                        ministerio_id=m_id,
                        participante_id=p_id,
                        funcao_id=f_id,
                        igreja_id=igreja_id
                    )
                    session.add(nova)
                    if instancia:
                        # ENVIAR MENSAGENS
                        nome = session.query(Participantes).get(p_id).nome.upper()
                        evento_obj = session.query(Eventos).get(evento)
                        evento_nome = evento_obj.nome
                        evento_data = evento_obj.data.strftime('%d/%m/%Y')
                        evento_hora = evento_obj.hora.strftime('%H:%M') if evento_obj.hora else "Não especificada"
                        ministerio_nome = session.query(Ministerios).get(m_id).nome.upper()
                        funcao_nome = session.query(Funcoes).get(f_id).nome
                        igreja_nome = session.query(Igrejas).get(igreja_id).nome.upper()

                        responsavel_telefone = st.session_state.telefone
                        link_responsavel = f"https://api.whatsapp.com/send?phone={responsavel_telefone}"

                        texto = (
                            f"🔄 *ESCALA ALTERADA*!\n\n"
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
                        
                        evento_datetime = datetime.combine(evento_obj.data, evento_obj.hora)

                        # 2 dias antes
                        scheduler.add_job(
                            enviar_lembrete,
                            'date',
                            run_date=evento_datetime - timedelta(days=2),
                            args=[p_id, evento_obj.id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "2dias", instancia]
                        )

                        # 1 dia antes
                        scheduler.add_job(
                            enviar_lembrete,
                            'date',
                            run_date=evento_datetime - timedelta(days=1),
                            args=[p_id, evento_obj.id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "1dia", instancia]
                        )

                        # 2 horas antes
                        scheduler.add_job(
                            enviar_lembrete,
                            'date',
                            run_date=evento_datetime - timedelta(hours=2),
                            args=[p_id, evento_obj.id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "2horas", instancia]
                        )
                        st.toast('Escala atualizada com sucesso!', icon='✅')
                        time.sleep(2)
                        # st.switch_page(os.path.join('Paginas','Eventos','Eventos.py'))

                # 5. Atualizar descrição geral
                desc_obj = session.query(DescricaoEscala).filter_by(
                    igreja_id=igreja_id,
                    evento_id=evento,
                    ministerio_id=ministerio
                ).first()
                
                if desc_obj:
                    desc_obj.descricao = descricao
                else:
                    nova_desc = DescricaoEscala(
                        igreja_id=igreja_id,
                        evento_id=evento,
                        ministerio_id=ministerio,
                        descricao=descricao,
                    )
                    session.add(nova_desc)

                # 6. Commit
                session.commit()
                del st.session_state.lista_participante_escala_funcao
                st.toast('Escala atualizada com sucesso!', icon='✅')
                
            except Exception as e:
                session.rollback()
                st.error(f'Erro ao atualizar: {e}')
                
        deletar = st.button('Deletar', key='danger')
        if deletar:
            @st.dialog('Confirmar Exclusão')
            def msg_confirmacao():
                ministerio_name = session.query(Ministerios).get(ministerio)
                st.write(f'deseja excluir a escala: **{ministerio_name.nome}**')
                with st.container(horizontal=True):
                    if st.button('Confirmar', type='primary'):

                        session.query(Escalas).filter_by(
                            igreja_id=igreja_id,
                            evento_id=evento,
                            ministerio_id=ministerio
                        ).delete()
                        session.query(DescricaoEscala).filter_by(
                            igreja_id=igreja_id,
                            evento_id=evento,
                            ministerio_id=ministerio
                        ).delete()
                        session.commit()
                        st.success("Escala cadastrada com sucesso!")
                        time.sleep(2)
                        del st.session_state.lista_participante_escala_funcao
                        st.switch_page(os.path.join('Paginas','Eventos','Eventos.py'))
                    if st.button('Cancelar'):
                        st.rerun()
                

            msg_confirmacao()
session.close()