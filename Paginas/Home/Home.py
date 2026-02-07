import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sarça",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon='sarca2.png'
)

# Estilo customizado (opcional)
st.markdown("""
    <style>
    .titulo {
        font-size: 48px;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
    }
    .subtitulo {
        font-size: 20px;
        color: #555;
        text-align: center;
    }
    .rodape {
        font-size: 14px;
        color: #888;
        text-align: center;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# Conteúdo da tela inicial
with st.container(horizontal_alignment='center'):
    st.image("sarca2.png", width=200)
# with st.container(horizontal_alignment='center'):
st.markdown('<div class="titulo">Bem-vindo ao Sarça</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Um espaço onde o chamado se encontra com a organização</div>', unsafe_allow_html=True)

st.divider()

st.write("Este aplicativo web foi criado para apoiar sua comunidade na gestão de **eventos**, **escalas** e **liturgias** com clareza e propósito.")
st.write("Assim como Moisés foi chamado na sarça ardente, aqui você encontra ferramentas para servir com excelência.")

st.divider()

st.markdown('<div class="rodape">© 2026 Sarça - Desenvolvido para fortalecer sua missão</div>', unsafe_allow_html=True)