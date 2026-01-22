import streamlit as st
from db import SessionLocal
from models import Participantes, Usuarios, Ministerios, Funcoes

st.set_page_config(layout='centered')
session = SessionLocal()

st.title("📋 Cadastro de Participantes")

# Buscar usuários, ministérios e funções da igreja
usuarios = session.query(Usuarios).filter_by(igreja_id=st.session_state.igreja).all()
ministerios = session.query(Ministerios).filter_by(igreja_id=st.session_state.igreja).all()
funcoes = session.query(Funcoes).filter_by(igreja_id=st.session_state.igreja).all()

opcoes_usuarios = ["Convidado"] + [f"{u.id} - {u.nome}" for u in usuarios]

with st.container(border=True):
    escolha = st.selectbox("Selecione um usuário ou digite novo:", options=opcoes_usuarios, index=None)

    nome_extra = None
    if escolha == "Convidado":
        nome_extra = st.text_input("Nome do convidado")

    telefone = st.text_input("Telefone")

    # Seleção de ministérios e funções
    ministerios_escolhidos = st.multiselect(
        "Selecione os ministérios",
        options=[f"{m.id} - {m.nome}" for m in ministerios]
    )

    funcoes_escolhidas = st.multiselect(
        "Selecione as funções",
        options=[f"{f.id} - {f.nome}" for f in funcoes]
    )

    salvar = st.button("Cadastrar", type="primary")

    if salvar:
        try:
            if escolha == "Convidado":
                if not nome_extra or nome_extra.strip() == "":
                    st.error("⚠️ O nome do convidado não pode estar vazio.")
                else:
                    novo_participante = Participantes(
                        usuario_id=None,
                        nome=nome_extra.strip(),
                        igreja_id=st.session_state.igreja,
                        telefone='55'+telefone.strip(),
                    )
            else:
                usuario_id = int(escolha.split(" - ")[0])
                usuario_nome = session.query(Usuarios).get(usuario_id).nome
                novo_participante = Participantes(
                    usuario_id=usuario_id,
                    igreja_id=st.session_state.igreja,
                    nome=usuario_nome,
                    telefone=telefone.strip(),
                )

            # Adicionar ministérios
            for mid in ministerios_escolhidos:
                m_id = int(mid.split(" - ")[0])
                ministerio = session.query(Ministerios).get(m_id)
                novo_participante.ministerios.append(ministerio)

            # Adicionar funções
            for fid in funcoes_escolhidas:
                f_id = int(fid.split(" - ")[0])
                funcao = session.query(Funcoes).get(f_id)
                novo_participante.funcoes.append(funcao)

            session.add(novo_participante)
            session.commit()

            st.success(f"Participante '{novo_participante.nome}' cadastrado com sucesso!")
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao cadastrar Participante: {e}")
        finally:
            session.close()