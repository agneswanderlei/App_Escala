import streamlit as st
import os
import streamlit_authenticator as stauth
from models import Usuarios, Igrejas
from db import SessionLocal
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# --- Configuração Inicial ---
st.set_page_config(
    page_title="Sarça", 
    initial_sidebar_state='collapsed', 
    page_icon='sarca2.png'
)

session = SessionLocal()

# Inicializa o scheduler apenas uma vez
if "scheduler" not in st.session_state:
    jobstores = {
        'default': SQLAlchemyJobStore(url='sqlite:///Banco_dados/jobs.sqlite')
    }
    st.session_state.scheduler = BackgroundScheduler(jobstores=jobstores)
    st.session_state.scheduler.start()

# consultar banco usuarios
usuarios = session.query(Usuarios).all()
if len(usuarios) == 0:
    igreja = session.query(Igrejas).filter_by(nome='global').first()
    if not igreja:
        igreja = Igrejas(nome='global')
        session.add(igreja)
        session.commit()

    admin_user = Usuarios(
        nome='Admin',
        cpf='777',
        password=stauth.Hasher.hash('1012ar1987'),
        perfil='Supervisor',
        igreja_id=igreja.id
    )
    session.add(admin_user)
    session.commit()
    session.close()
    st.success('Supervisor adicionado com sucesso!')
    usuarios = session.query(Usuarios).all()

credenciais = {
    "usernames": {
        usuario.cpf: {
            "nome": usuario.nome,
            "password": usuario.password,
            "perfil": usuario.perfil,
            "igreja_id": usuario.igreja_id
        } for usuario in usuarios
    }
}

authenticator = stauth.Authenticate(
    credentials=credenciais,
    cookie_name="Florescer",
    cookie_key="Florescer_key",
    cookie_expiry_days=1
)

pages = {
    'Home': [os.path.join('Paginas','Home','Home.py')],
    'Igrejas': [
        os.path.join('Paginas','Igrejas','Igrejas.py'),
        os.path.join('Paginas','Igrejas','Adicionar_Igreja.py'),
        os.path.join('Paginas','Igrejas','Editar_Igreja.py'),
    ],
    'Grupos': [
        os.path.join('Paginas','Grupos','Grupos.py'),
        os.path.join('Paginas','Grupos','Adicionar_Grupo.py'),
        os.path.join('Paginas','Grupos','Editar_Grupo.py'),
    ],
    'Funções': [
        os.path.join('Paginas','Funcoes','Funções.py'),
        os.path.join('Paginas','Funcoes','Adicionar_Função.py'),
        os.path.join('Paginas','Funcoes','Editar_Função.py'),
    ],
    'Participantes': [
        os.path.join('Paginas','Participantes','Participantes.py'),
        os.path.join('Paginas','Participantes','Adicionar_Participante.py'),
        os.path.join('Paginas','Participantes','Editar_Participante.py'),
    ],
    'Indisponibilidades': [
        os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'),
        os.path.join('Paginas','Indisponibilidade','Adicionar_Indisponibilidade.py'),
        os.path.join('Paginas','Indisponibilidade','Editar_Indisponibilidade.py'),
    ],
    'Eventos': [
        os.path.join('Paginas','Eventos','Eventos.py'),
        os.path.join('Paginas','Eventos','Adicionar_Evento.py'),
        os.path.join('Paginas','Eventos','Editar_Evento.py'),
    ],
    'Escalas': [
        os.path.join('Paginas','Escalas','Minhas_Escalas.py'),
        os.path.join('Paginas','Escalas','Adicionar_Escala.py'),
        os.path.join('Paginas','Escalas','Editar_Escala.py'),
    ],
    'Liturgia': [
        os.path.join('Paginas','Liturgias','Adicionar_Liturgia.py'),
        os.path.join('Paginas','Liturgias','Editar_Liturgia.py'),
    ],
    'Usuários': [
        os.path.join('Paginas','Usuarios','Home_Usuários.py'),
        os.path.join('Paginas','Usuarios','Adicionar_Usuários.py'),
        os.path.join('Paginas','Usuarios','Editar_Contato.py'),
        os.path.join('Paginas','Usuarios','Editar_Perfil.py'),
        os.path.join('Paginas','Usuarios','Editar_Senha.py'),
        os.path.join('Paginas','Usuarios','Excluir_Usuários.py'),
    ]
}

# ============================================
# TELA DE LOGIN (NÃO AUTENTICADO)
# ============================================
if not st.session_state.get('authentication_status'):
    # COLUNAS APENAS PARA A TELA DE LOGIN
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("sarca2.png", width=600)
    
    with col2:
        st.markdown("<h2>🔥 Bem-vindo ao Sarça</h2>", unsafe_allow_html=True)
        st.write("Aqui você pode gerenciar **eventos**, **escalas** e **liturgias** de forma simples e intuitiva.")
        st.write("Faça login para acessar as funcionalidades.")
        authenticator.login(captcha=False, max_login_attempts=3)

# ============================================
# SISTEMA (AUTENTICADO)
# ============================================
elif st.session_state.get('authentication_status'):
    cpf_logado = st.session_state['username']
    usuario_logado = session.query(Usuarios).filter_by(cpf=cpf_logado).first()

    st.session_state['perfil'] = usuario_logado.perfil
    st.session_state['nome'] = usuario_logado.nome
    st.session_state['telefone'] = usuario_logado.telefone
    st.session_state['igreja'] = usuario_logado.igreja_id
    st.session_state['user_id'] = usuario_logado.id 

    nome_igreja = session.query(Igrejas).get(st.session_state.igreja)
    
    with st.sidebar:
        st.markdown("### 👤 Usuário Logado")
        st.write(f"**Nome:** {st.session_state.nome}")
        st.write(f"**Perfil:** {st.session_state.perfil}")
        st.write(f"**Igreja:** {nome_igreja.nome}")

    perfil_usuario = credenciais['usernames'][st.session_state['username']]['perfil']
    st.session_state['perfil'] = perfil_usuario
    
    if perfil_usuario == 'Supervisor':
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
        
    elif perfil_usuario == 'Administrador':
        pages_admin = {
            'Home': [os.path.join('Paginas','Home','Home.py')],
            'Grupos': [
                os.path.join('Paginas','Grupos','Grupos.py'),
                os.path.join('Paginas','Grupos','Adicionar_Grupo.py'),
                os.path.join('Paginas','Grupos','Editar_Grupo.py'),
            ],
            'Funções': [
                os.path.join('Paginas','Funcoes','Funções.py'),
                os.path.join('Paginas','Funcoes','Adicionar_Função.py'),
                os.path.join('Paginas','Funcoes','Editar_Função.py'),
            ],
            'Participantes': [
                os.path.join('Paginas','Participantes','Participantes.py'),
                os.path.join('Paginas','Participantes','Adicionar_Participante.py'),
                os.path.join('Paginas','Participantes','Editar_Participante.py'),
            ],
            'Indisponibilidades': [
                os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'),
                os.path.join('Paginas','Indisponibilidade','Adicionar_Indisponibilidade.py'),
                os.path.join('Paginas','Indisponibilidade','Editar_Indisponibilidade.py'),
            ],
            'Eventos': [
                os.path.join('Paginas','Eventos','Eventos.py'),
                os.path.join('Paginas','Eventos','Adicionar_Evento.py'),
                os.path.join('Paginas','Eventos','Editar_Evento.py'),
            ],
            'Escalas': [
                os.path.join('Paginas','Escalas','Minhas_Escalas.py'),
                os.path.join('Paginas','Escalas','Adicionar_Escala.py'),
                os.path.join('Paginas','Escalas','Editar_Escala.py'),
            ],
            'Liturgia': [
                os.path.join('Paginas','Liturgias','Adicionar_Liturgia.py'),
                os.path.join('Paginas','Liturgias','Editar_Liturgia.py'),
            ],
            'Usuários': [
                os.path.join('Paginas','Usuarios','Home_Usuários.py'),
                os.path.join('Paginas','Usuarios','Adicionar_Usuários.py'),
                os.path.join('Paginas','Usuarios','Editar_Contato.py'),
                os.path.join('Paginas','Usuarios','Editar_Perfil.py'),
                os.path.join('Paginas','Usuarios','Editar_Senha.py'),
                os.path.join('Paginas','Usuarios','Excluir_Usuários.py'),
            ]
        }
        pg = st.navigation(pages_admin, position='top', expanded=False)
        pg.run()
        
    elif perfil_usuario == 'Líder':
        pages_lider = {
            'Home': [os.path.join('Paginas','Home','Home.py')],
            'Indisponibilidades': [
                os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'),
                os.path.join('Paginas','Indisponibilidade','Adicionar_Indisponibilidade.py'),
                os.path.join('Paginas','Indisponibilidade','Editar_Indisponibilidade.py'),
            ],
            'Eventos': [
                os.path.join('Paginas','Eventos','Eventos.py'),
                os.path.join('Paginas','Eventos','Adicionar_Evento.py'),
                os.path.join('Paginas','Eventos','Editar_Evento.py'),
            ],
            'Escalas': [
                os.path.join('Paginas','Escalas','Minhas_Escalas.py'),
                os.path.join('Paginas','Escalas','Adicionar_Escala.py'),
                os.path.join('Paginas','Escalas','Editar_Escala.py'),
            ],
            'Funções': [os.path.join('Paginas','Funcoes','Funções.py')],
            'Liturgia': [
                os.path.join('Paginas','Liturgias','Adicionar_Liturgia.py'),
                os.path.join('Paginas','Liturgias','Editar_Liturgia.py'),
            ],
            'Usuários': [os.path.join('Paginas','Usuarios','Editar_Senha.py')]
        }
        pg = st.navigation(pages_lider, position='top', expanded=False)
        pg.run()
        
    else:  # Participante
        pages_participante = {
            'Home': [os.path.join('Paginas','Home','Home.py')],
            'Indisponibilidades': [
                os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'),
                os.path.join('Paginas','Indisponibilidade','Adicionar_Indisponibilidade.py'),
                os.path.join('Paginas','Indisponibilidade','Editar_Indisponibilidade.py'),
            ],
            'Eventos': [os.path.join('Paginas','Eventos','Eventos.py')],
            'Escalas': [os.path.join('Paginas','Escalas','Minhas_Escalas.py')],
            'Funções': [os.path.join('Paginas','Funcoes','Funções.py')],
            'Usuários': [os.path.join('Paginas','Usuarios','Editar_Senha.py')]
        }
        pg = st.navigation(pages_participante, position='top', expanded=False)
        pg.run()
    
    authenticator.logout('Sair', location='sidebar', use_container_width=False)

# ============================================
# MENSAGENS DE ERRO
# ============================================
elif st.session_state.get('authentication_status') is False:
    st.error('🚫 Login inválido. Verifique as credenciais.')
elif st.session_state.get('authentication_status') is None:
    st.warning('Os campos devem ser preenchidos antes de continuar.')