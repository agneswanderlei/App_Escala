# jobs.py
from db import SessionLocal
from models import Participantes, Eventos
from Paginas.Escalas.Enviar_mensagens import send_whatsapp_message
def enviar_lembrete(p_id, evento_id, ministerio_nome, funcao_nome, igreja_nome, link_responsavel, tipo, instancia):
    session = SessionLocal()
    participante = session.query(Participantes).get(p_id)
    evento_obj = session.query(Eventos).get(evento_id)

    if tipo == "2dias":
        titulo = "⏰ Faltam 2 dias para sua escala!"
    elif tipo == "1dia":
        titulo = "⏰ Faltam 1 dia para sua escala!"
    elif tipo == "2horas":
        titulo = "⏰ Faltam 2 horas para sua escala!"
    else:
        titulo = "📣 Lembrete de escala!"

    texto = (
        f"{titulo}\n\n"
        f"🏛️ *Igreja:* {igreja_nome}\n"
        f"🗓️ *Evento:* {evento_obj.nome}\n"
        f"📅 *Data:* {evento_obj.data.strftime('%d/%m/%Y')}\n"
        f"⏰ *Horário:* {evento_obj.hora.strftime('%H:%M')}\n"
        f"🙌 *Ministério:* {ministerio_nome}\n"
        f"👤 *Função:* {funcao_nome}\n\n"
        f"⚠️ Caso não possa comparecer, fale diretamente com o responsável:\n"
        f"{link_responsavel}\n\n"
        f"Equipe {igreja_nome}"
    )

    send_whatsapp_message(participante.telefone, texto, instancia)