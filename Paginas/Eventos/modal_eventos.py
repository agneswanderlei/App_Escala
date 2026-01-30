import streamlit as st
from db import SessionLocal
from models import DescricaoEscala
from collections import defaultdict

session = SessionLocal()

def detalhes(evento, escalas, descricao):
    tab1, tab2 = st.tabs(['Geral', 'Escala'])
    
    with tab1:
        st.write(f"**Igreja:** {evento['extendedProps'].get('igreja', '-')}")
        st.write(f"**Nome:** {evento['title']}")
        st.write(f"**Data:** {evento['extendedProps']['data_formatada']}")
        st.write(f"**Hora:** {evento['extendedProps']['hora_formatada']}")
        st.write(f"**Descrição:** {evento['extendedProps'].get('descricao', '-')}")

    with tab2:
        if not escalas:
            st.info("Nenhuma escala cadastrada para este evento.")
        else:
            # Agrupar escalas por ministério
            escalas_por_ministerio = defaultdict(list)
            for esc in escalas:
                escalas_por_ministerio[esc.ministerio.nome].append(esc)
            
            # Exibir cada ministério uma vez
            for ministerio_nome, escalas_ministerio in escalas_por_ministerio.items():
                with st.expander(f'{ministerio_nome}'):
                    # Pegar a descrição (todas as escalas do mesmo ministério têm a mesma descrição)
                    primeira_escala = escalas_ministerio[0]
                    desc = session.query(DescricaoEscala).filter_by(
                        ministerio_id=primeira_escala.ministerio_id,
                        evento_id=primeira_escala.evento_id
                    ).first()
                    # Listar todos os participantes deste ministério
                    for esc in escalas_ministerio:
                        st.write(f"**{esc.funcao.nome}:** {esc.participante.nome if hasattr(esc, 'participante') else '-'}")

                    if desc:
                        st.write(f"**Descrição:** {desc.descricao}")