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
            padding-top: 1rem;
        }
        h1 {
            margin-top: 0;
        }
    </style>
""", unsafe_allow_html=True)
# consultar banco usuarios
usuarios = session.query(Usuarios).all()
if len(usuarios) == 0:
    # Add igreja global
    igreja =Igrejas(nome='global')
    session.add(igreja)
    session.commit()
    admin_user = Usuarios(
        nome='Admin',
        cpf='777',
        password=stauth.Hasher.hash('1012ar1987'),
        perfil='Administrador',
        igreja_id=igreja.id
    )
    session.add(admin_user)
    session.commit()
    session.close()
    st.success('Administrador adicionado com sucesso!')
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
        os.path.join('Paginas','Igrejas','Home_Igreja.py'),
        os.path.join('Paginas','Igrejas','Adicionar_Igreja.py'),
        os.path.join('Paginas','Igrejas','Editar_Igreja.py'),

    ],
    'Funcoes': [
        os.path.join('Paginas','Funcoes','Home_Funcao.py'),
        os.path.join('Paginas','Funcoes','Adicionar_Funcao.py'),
        os.path.join('Paginas','Funcoes','Editar_Funcao.py'),

    ],
    'Usuários': [
        os.path.join('Paginas','Usuarios','Home_Usuarios.py'),
        os.path.join('Paginas','Usuarios','Adicionar_Usuarios.py'),
        os.path.join('Paginas','Usuarios','Editar_Perfil.py'),
        os.path.join('Paginas','Usuarios','Editar_Senha.py'),
        os.path.join('Paginas','Usuarios','Excluir_Usuarios.py'),

    ]
}


authenticator.login(captcha=False, max_login_attempts=3)

if st.session_state.get('authentication_status'):
    perfil_usuario = credenciais['usernames'][st.session_state['username']]['perfil']
    st.session_state.perfil = credenciais['usernames'][st.session_state['username']]['perfil']
    st.session_state.nome = credenciais['usernames'][st.session_state['username']]['nome']
    st.session_state.igreja = credenciais['usernames'][st.session_state['username']]['igreja_id']
    nome_igreja = session.query(Igrejas).get(st.session_state.igreja)
    with st.sidebar:
        st.markdown("### 👤 Usuário Logado")
        st.write(f"**Nome:** {st.session_state.nome}")
        st.write(f"**Perfil:** {st.session_state.perfil}")
        st.write(f"**Igreja:** {nome_igreja.nome}")

    perfil_usuario = credenciais['usernames'][st.session_state['username']]['perfil']
    st.session_state['perfil'] = perfil_usuario
    if perfil_usuario == 'Administrador':
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
    elif perfil_usuario == 'Líder':
        # pages = {
        #     'Home': [
        #         os.path.join('Paginas','Home','Home.py')
        #     ],
        #     'Usuários': [
        #         os.path.join('paginas','Usuarios','Home_Usuarios.py'),
        #         os.path.join('paginas','Usuarios','Adicionar_Usuarios.py'),
        #         # os.path.join('paginas','Usuarios','Editar_Perfil.py'),
        #         # os.path.join('paginas','Usuarios','Editar_Senha.py'),
        #         # os.path.join('paginas','Usuarios','Excluir_Usuarios.py'),

        #     ]
        # }
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
    else:
        pages = {
            'Home': [
                os.path.join('Paginas','Home','Home.py')
            ],
            
        }
        pg = st.navigation(pages, position='top', expanded=False)
        pg.run()
    authenticator.logout('Sair', location='sidebar', use_container_width=False)
elif st.session_state.get('authentication_status') is False:
    st.error('🚫 Login inválido. Verifique as credenciais.')
elif st.session_state.get('authentication_status') is None:
    st.warning('Os campos devem ser preenchidos antes de continuar.')