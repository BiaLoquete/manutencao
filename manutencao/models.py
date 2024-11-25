from app import db
from enum import Enum
from datetime import datetime


class Cargo(Enum):
    funcionario_geral = "funcionario_geral"
    funcionario_manutencao = "funcionario_manutencao"
    chefe_manutencao = "chefe_manutencao"


class Prioridade(Enum):
    Baixa = 'Baixa'
    Media = 'Media'
    Alta = 'Alta'


class Status(Enum):
    Aberto = "Aberto"
    Em_andamento = "Em andamento"
    Fechado = "Fechado"


class Funcionario(db.Model):

    id_funcionario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    nif = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.Enum(Cargo), nullable=False)

    problemas = db.relationship('Problema', backref='funcionario', lazy=True)


class Problema(db.Model):
    caminho_imagem = db.Column(db.String(255), nullable=True)
    id_problema = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=True)
    local = db.Column(db.String(255), nullable=True)
    prontuario = db.Column(db.Integer, nullable=True)
    prioridade = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum(Status), default=Status.Aberto, nullable=False)  # Default é "Aberto"
    obs_funcionario = db.Column(db.String(255), nullable=True)
    datetime_inicio = db.Column(db.DateTime, nullable=True)
    datetime_finalizado = db.Column(db.DateTime, nullable=True)
    quanto_gastou = db.Column(db.Numeric(10, 2), nullable=True)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('funcionario.id_funcionario'), nullable=True)
class Materiais(db.Model):

    id_material = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    unidade = db.Column(db.String(255), nullable=False)
    quantidade_estoque = db.Column(db.Numeric(10, 2), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)


class ProblemaMaterial(db.Model):

    id_problema_material = db.Column(db.Integer, primary_key=True)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('funcionario.id_funcionario'))
    id_problema = db.Column(db.Integer, db.ForeignKey('problema.id_problema'))
    id_material = db.Column(db.Integer, db.ForeignKey('materiais.id_material'))
    quantidade = db.Column(db.Integer)
    valor_total = db.Column(db.Numeric(10, 2))

    funcionario = db.relationship('Funcionario', backref='problema_material', lazy=True)
    problema = db.relationship('Problema', backref='problema_material', lazy=True)
    material = db.relationship('Materiais', backref='problema_material', lazy=True)

# Se um funcionário pode estar associado a vários problemas e um problema pertence a um funcionário, você pode usar back_populates para criar uma relação bidirecional.