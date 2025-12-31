import streamlit as st
from db import SessionLocal
from models import Participantes, Usuarios

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Cadastro de Participantes")

# Buscar usuários da igreja
usuarios = session.query(Usuarios).filter_by(igreja_id=st.session_state.igreja).all()
opcoes = ["Convidado"] + [f"{u.id} - {u.nome}" for u in usuarios]

with st.container(border=True):
    escolha = st.selectbox("Selecione um usuário ou digite novo:", options=opcoes, index=None)

    # Se escolher "Convidado", abre campo de texto para nome
    nome_extra = None
    if escolha == "Convidado":
        nome_extra = st.text_input("Nome do participante externo")
    
    telefone = st.text_input("Telefone")

    salvar = st.button("Cadastrar", type="primary")

    if salvar:
        try:
            if escolha == "Convidado":
                if not nome_extra or nome_extra.strip() == "":
                    st.error("⚠️ O nome do participante externo não pode estar vazio.")
                else:
                    novo_participante = Participantes(
                        usuario_id=None,
                        nome=nome_extra.strip(),
                        igreja_id=st.session_state.igreja,
                        telefone=telefone.strip(),
                    )
                    # Aqui você pode salvar o nome_extra em Participantes se tiver campo `nome`
                    # ou apenas exibir como referência
                    st.success(f"Participante externo '{nome_extra}' cadastrado com sucesso!")
            else:
                usuario_id = int(escolha.split(" - ")[0])
                novo_participante = Participantes(
                    usuario_id=usuario_id,
                    igreja_id=st.session_state.igreja,
                    nome=session.query(Usuarios).get(usuario_id).nome,
                    telefone=telefone.strip(),
                )
                usuario_nome = session.query(Usuarios).get(usuario_id).nome
                st.success(f"Participante vinculado ao usuário '{usuario_nome}' cadastrado com sucesso!")

            session.add(novo_participante)
            session.commit()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao cadastrar Participante: {e}")
        finally:
            session.close()