import streamlit as st
import os
import streamlit_authenticator as stauth
from models import Usuarios, Igrejas
from db import SessionLocal
# --- Configuração Inicial ---
st.set_page_config(page_title="FLORESCER", initial_sidebar_state='collapsed')
# --- Configuração do Autenticador ---
session = SessionLocal()
# reduz espaços no topo
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
        h1 {
            margin-top: 100;
        }
    </style>
""", unsafe_allow_html=True)
# consultar banco usuarios
usuarios = session.query(Usuarios).all()
if len(usuarios) == 0:
    # Verifica se já existe igreja 'global'
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
    'Home': [
        os.path.join('Paginas','Home','Home.py')
    ],
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
        # os.path.join('Paginas','Escalas','Escalas.py'),
        os.path.join('Paginas','Escalas','Adicionar_Escala.py'),
        os.path.join('Paginas','Escalas','Editar_Escala.py'),
    ],
    'Usuários': [
        os.path.join('Paginas','Usuarios','Home_Usuários.py'),
        os.path.join('Paginas','Usuarios','Adicionar_Usuários.py'),
        os.path.join('Paginas','Usuarios','Editar_Perfil.py'),
        os.path.join('Paginas','Usuarios','Editar_Senha.py'),
        os.path.join('Paginas','Usuarios','Excluir_Usuários.py'),

    ]
}


authenticator.login(captcha=False, max_login_attempts=3)

if st.session_state.get('authentication_status'):
    cpf_logado = st.session_state['username']
    usuario_logado = session.query(Usuarios).filter_by(cpf=cpf_logado).first()

    st.session_state['perfil'] = usuario_logado.perfil
    st.session_state['nome'] = usuario_logado.nome
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
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
    elif perfil_usuario == 'Líder':
        pages = {
            'Home': [
                os.path.join('Paginas','Home','Home.py')
            ],
            'Usuários': [
                os.path.join('paginas','Usuarios','Home_Usuários.py'),
                os.path.join('paginas','Usuarios','Adicionar_Usuários.py'),
                # os.path.join('paginas','Usuarios','Editar_Perfil.py'),
                # os.path.join('paginas','Usuarios','Editar_Senha.py'),
                # os.path.join('paginas','Usuarios','Excluir_Usuarios.py'),

            ]
        }
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
    else:
        pages = {
            'Home': [
                os.path.join('Paginas','Home','Home.py')
            ],
            'Indisponibilidades': [
                os.path.join('Paginas','Indisponibilidade','Indisponibilidades.py'),
                os.path.join('Paginas','Indisponibilidade','Adicionar_Indisponibilidade.py'),
                os.path.join('Paginas','Indisponibilidade','Editar_Indisponibilidade.py'),
            ],
            'Usuários': [
                os.path.join('paginas','Usuarios','Home_Usuários.py'),
                # os.path.join('paginas','Usuarios','Adicionar_Usuários.py'),
                # os.path.join('paginas','Usuarios','Editar_Perfil.py'),
                os.path.join('paginas','Usuarios','Editar_Senha.py'),
                # os.path.join('paginas','Usuarios','Excluir_Usuarios.py'),

            ]
        }
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
    authenticator.logout('Sair', location='sidebar', use_container_width=False)
elif st.session_state.get('authentication_status') is False:
    st.error('🚫 Login inválido. Verifique as credenciais.')
elif st.session_state.get('authentication_status') is None:
    st.warning('Os campos devem ser preenchidos antes de continuar.')