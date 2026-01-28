import streamlit as st

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
            for esc in escalas:
                with st.expander(f'{esc.ministerio.nome}'):
                    # Aqui você pode adicionar mais detalhes da escala
                    st.write(f"**Escalados:** {esc.participante.nome if hasattr(esc, 'participante') else '-'}")
                    # Adicione outros campos conforme seu modelo
                    
                    st.write(f"**Descrição:** {descricao.descricao}")