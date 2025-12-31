from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Time
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Associação muitos-para-muitos entre membros e ministérios
membro_ministerio = Table(
    "membro_ministerio",
    Base.metadata,
    Column("membro_id", Integer, ForeignKey("membros.id")),
    Column("ministerio_id", Integer, ForeignKey("ministerios.id"))
)

# Associação muitos-para-muitos entre membros e funções
membro_funcao = Table(
    "membro_funcao",
    Base.metadata,
    Column("membro_id", Integer, ForeignKey("membros.id")),
    Column("funcao_id", Integer, ForeignKey("funcoes.id"))
)

class Funcoes(Base):
    __tablename__ = "funcoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    membros = relationship("Membros", secondary=membro_funcao, back_populates="funcoes")
    igreja = relationship('Igrejas', back_populates='funcoes')

class Igrejas(Base):
    __tablename__ = "igrejas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)

    usuarios = relationship("Usuarios", back_populates="igreja")
    membros = relationship("Membros", back_populates="igreja")
    ministerios = relationship("Ministerios", back_populates="igreja")
    eventos = relationship("Eventos", back_populates="igreja")
    funcoes = relationship("Funcoes", back_populates='igreja')


class Usuarios(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    perfil = Column(String, nullable=False)  # admin, lider, membro
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="usuarios")
    membro = relationship("Membros", uselist=False, back_populates="usuario")


class Indisponibilidades(Base):
    __tablename__ = "indisponibilidades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    membro_id = Column(Integer, ForeignKey("membros.id"), nullable=False)
    data = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=True)
    hora_fim = Column(Time, nullable=True)
    motivo = Column(String, nullable=True)

    membro = relationship("Membros", back_populates="indisponibilidades")


class Membros(Base):
    __tablename__ = "membros"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), unique=True)
    igreja_id = Column(Integer, ForeignKey("igrejas.id", ondelete="CASCADE"), nullable=False)

    usuario = relationship("Usuarios", back_populates="membro")
    igreja = relationship("Igrejas", back_populates="membros")
    ministerios = relationship("Ministerios", secondary=membro_ministerio, back_populates="membros")
    indisponibilidades = relationship("Indisponibilidades", back_populates="membro")
    funcoes = relationship("Funcoes", secondary=membro_funcao, back_populates="membros")


class Ministerios(Base):
    __tablename__ = "ministerios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="ministerios")
    membros = relationship("Membros", secondary=membro_ministerio, back_populates="ministerios")
    escalas = relationship("Escalas", back_populates="ministerio")


class Eventos(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    data = Column(Date, nullable=False)
    igreja_id = Column(Integer, ForeignKey("igrejas.id"), nullable=False)

    igreja = relationship("Igrejas", back_populates="eventos")
    escalas = relationship("Escalas", back_populates="evento")


class Escalas(Base):

    __tablename__ = "escalas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"))
    ministerio_id = Column(Integer, ForeignKey("ministerios.id"))
    membro_id = Column(Integer, ForeignKey("membros.id"))
    funcao_id = Column(Integer, ForeignKey("funcoes.id"))  # referência à tabela Funcoes

    evento = relationship("Eventos", back_populates="escalas")
    ministerio = relationship("Ministerios", back_populates="escalas")
    membro = relationship("Membros")
    funcao = relationship("Funcoes")  # relação direta com Funcoes

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
    responsavel_id = Column(Integer, ForeignKey("membros.id"), nullable=True)  # quem conduz

    liturgia_id = Column(Integer, ForeignKey("liturgias.id"), nullable=False)
    liturgia = relationship("Liturgias", back_populates="momentos")
    responsavel = relationship("Membros")  # membro responsável
