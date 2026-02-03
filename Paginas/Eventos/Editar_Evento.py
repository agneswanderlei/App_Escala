import streamlit as st
from db import SessionLocal
from models import Eventos, Escalas
import time
from datetime import datetime, timedelta
from Paginas.Escalas.jobs import enviar_lembrete
from models import Igrejas
st.set_page_config(layout='centered')
session = SessionLocal()
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("📋 Editar de Eventos")
if 'evento' not in st.session_state:
    st.session_state.evento = None

perfil = st.session_state.perfil
igreja_id = st.session_state.igreja
scheduler = st.session_state.scheduler  # ← ADICIONE ISSO

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

# ← GUARDAR DATA E HORA ORIGINAIS PARA COMPARAR
data_original = eventos.data
hora_original = eventos.hora

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
            # Verificar se data ou hora mudaram
            data_mudou = data != data_original
            hora_mudou = hora != hora_original
            
            # Atualizar evento
            eventos.nome = nome
            eventos.data = data
            eventos.hora = hora
            eventos.descricao = descricao
            session.commit()

            # SE DATA OU HORA MUDARAM, RECRIAR OS JOBS
            if data_mudou or hora_mudou:
                # 1. Buscar todos os participantes escalados neste evento
                escalas = session.query(Escalas).filter_by(evento_id=evento_selecionado).all()
                participantes_evento_ids = [esc.participante_id for esc in escalas]
                
                # 2. Remover todos os jobs deste evento
                jobs_existentes = scheduler.get_jobs()
                for job in jobs_existentes:
                    # Verificar se o job é deste evento
                    if (len(job.args) > 1 and 
                        job.args[1] == evento_selecionado and
                        job.args[0] in participantes_evento_ids):
                        scheduler.remove_job(job.id)
                
                # 3. Recriar jobs com nova data/hora
                evento_datetime = datetime.combine(data, hora)
                
                for esc in escalas:
                    p_id = esc.participante_id
                    ministerio_nome = esc.ministerio.nome.upper()
                    funcao_nome = esc.funcao.nome
                    igreja_nome = session.query(Igrejas).get(igreja_id).nome.upper()
                    responsavel_telefone = st.session_state.telefone
                    link_responsavel = f"https://api.whatsapp.com/send?phone={responsavel_telefone}"
                    instancia = session.query(Igrejas).get(igreja_id).instancia
                    
                    # 2 dias antes
                    scheduler.add_job(
                        enviar_lembrete,
                        'date',
                        run_date=evento_datetime - timedelta(minutes=2),
                        args=[p_id, evento_selecionado, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "2dias", instancia]
                    )

                    # 1 dia antes
                    scheduler.add_job(
                        enviar_lembrete,
                        'date',
                        run_date=evento_datetime - timedelta(minutes=1),
                        args=[p_id, evento_selecionado, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "1dia", instancia]
                    )

                    # 2 horas antes
                    scheduler.add_job(
                        enviar_lembrete,
                        'date',
                        run_date=evento_datetime - timedelta(minutes=2),
                        args=[p_id, evento_selecionado, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, "2horas", instancia]
                    )
                
                st.success(f"Evento '{eventos.nome}' atualizado com sucesso! Jobs reagendados.")
            else:
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
            
            with st.container(horizontal=True):
                if st.button("✅ Confirmar exclusão"):
                    try:
                        # REMOVER JOBS ANTES DE DELETAR O EVENTO
                        escalas = session.query(Escalas).filter_by(evento_id=evento_selecionado).all()
                        participantes_evento_ids = [esc.participante_id for esc in escalas]
                        
                        jobs_existentes = scheduler.get_jobs()
                        for job in jobs_existentes:
                            if (len(job.args) > 1 and 
                                job.args[1] == evento_selecionado and
                                job.args[0] in participantes_evento_ids):
                                scheduler.remove_job(job.id)
                        
                        # Deletar evento (cascata vai deletar escalas)
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