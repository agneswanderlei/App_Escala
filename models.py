from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Time
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Associação muitos-para-muitos entre participantes e ministérios
participante_ministerio = Table(
    "participante_ministerio",
    Base.metadata,
    Column("participante_id", Integer, ForeignKey("participantes.id")),
    Column("ministerio_id", Integer, ForeignKey("ministerios.id"))
)

# Associação muitos-para-muitos entre participantes e funções
participante_funcao = Table(
    "participante_funcao",
    Base.metadata,
    Column("participante_id", Integer, ForeignKey("participantes.id")),
    Column("funcao_id", Integer, ForeignKey("funcoes.id"))
)

class Funcoes(Base):
    __tablename__ = "funcoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    participantes = relationship("Participantes", secondary=participante_funcao, back_populates="funcoes")
    igreja = relationship('Igrejas', back_populates='funcoes')

class Igrejas(Base):
    __tablename__ = "igrejas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)

    usuarios = relationship("Usuarios", back_populates="igreja")
    participantes = relationship("Participantes", back_populates="igreja")
    ministerios = relationship("Ministerios", back_populates="igreja")
    eventos = relationship("Eventos", back_populates="igreja")
    escalas = relationship("Escalas", back_populates="igreja")
    funcoes = relationship("Funcoes", back_populates='igreja')
    liturgias = relationship("Liturgias", back_populates="igreja")
    indisponibilidades = relationship("Indisponibilidades", back_populates="igreja")

class Permissoes(Base):
    __tablename__ = "permissoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    pagina = Column(String, nullable=False)

    usuario = relationship("Usuarios", back_populates="permissoes")


class Usuarios(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    perfil = Column(String, nullable=False)  # admin, lider, parcipante
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="usuarios")
    participante = relationship("Participantes", uselist=False, back_populates="usuario")
    permissoes = relationship("Permissoes", back_populates="usuario", cascade="all, delete-orphan")


class Indisponibilidades(Base):
    __tablename__ = "indisponibilidades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"), nullable=False)
    data = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=True)
    hora_fim = Column(Time, nullable=True)
    motivo = Column(String, nullable=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    participante = relationship("Participantes", back_populates="indisponibilidades")
    igreja = relationship('Igrejas', back_populates='indisponibilidades')

class Participantes(Base):
    __tablename__ = "participantes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), unique=True, nullable=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    
    usuario = relationship("Usuarios", back_populates="participante")
    igreja = relationship("Igrejas", back_populates="participantes")
    ministerios = relationship("Ministerios", secondary=participante_ministerio, back_populates="participantes")
    indisponibilidades = relationship("Indisponibilidades", back_populates="participante")
    funcoes = relationship("Funcoes", secondary=participante_funcao, back_populates="participantes")
    escalas = relationship("Escalas", back_populates="participante")

class Ministerios(Base):
    __tablename__ = "ministerios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="ministerios")
    participantes = relationship("Participantes", secondary=participante_ministerio, back_populates="ministerios")
    escalas = relationship("Escalas", back_populates="ministerio")


class Eventos(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=True)
    descricao = Column(String, nullable=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="eventos")
    escalas = relationship("Escalas", back_populates="evento")
    liturgias = relationship("Liturgias", back_populates="evento")

class Escalas(Base):

    __tablename__ = "escalas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    ministerio_id = Column(Integer, ForeignKey("ministerios.id"))
    participante_id = Column(Integer, ForeignKey("participantes.id"))
    funcao_id = Column(Integer, ForeignKey("funcoes.id"))  # referência à tabela Funcoes
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="escalas")
    evento = relationship("Eventos", back_populates="escalas")
    ministerio = relationship("Ministerios", back_populates="escalas")
    participante = relationship("Participantes", back_populates="escalas")
    funcao = relationship("Funcoes")  # relação direta com Funcoes

class DescricaoEscala(Base):
    __tablename__ = "descricao_escala"
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    ministerio_id = Column(Integer, ForeignKey("ministerios.id"))
    igreja_id = Column(Integer, ForeignKey("igrejas.id"))
    descricao = Column(String, nullable=True)

    evento = relationship("Eventos")
    ministerio = relationship("Ministerios")
    igreja = relationship("Igrejas")

class Liturgias(Base):
    __tablename__ = "liturgias"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="liturgias")
    evento = relationship("Eventos", back_populates="liturgias")
    momentos = relationship("MomentosLiturgia", back_populates="liturgia", cascade="all, delete-orphan")

class MomentosLiturgia(Base):
    __tablename__ = "momentos_liturgia"
    id = Column(Integer, primary_key=True, autoincrement=True)
    horario = Column(Time, nullable=False)  # Ex: 09:00
    descricao = Column(String, nullable=False)  # Ex: "Louvor"
    responsavel_id = Column(Integer, ForeignKey("participantes.id"), nullable=True)  # quem conduz

    liturgia_id = Column(Integer, ForeignKey("liturgias.id"), nullable=False)
    liturgia = relationship("Liturgias", back_populates="momentos")
    responsavel = relationship("Participantes")  # participante responsável
