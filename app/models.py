from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default="voluntario")
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def definir_senha(self, senha_plana: str) -> None:
        self.senha_hash = generate_password_hash(senha_plana, method="pbkdf2:sha256")

    def verificar_senha(self, senha_plana: str) -> bool:
        return check_password_hash(self.senha_hash, senha_plana)


class Familia(db.Model):
    __tablename__ = "familia"
    id = db.Column(db.Integer, primary_key=True)
    nome_responsavel = db.Column(db.String(150), nullable=False)
    cpf_responsavel = db.Column(db.String(11), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(15), nullable=True)
    endereco_resumido = db.Column(db.String(200), nullable=False)
    qtd_integrantes = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(15), nullable=False, default="ativo")
    data_cadastro = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def cpf_mascarado(self) -> str:
        return f"***.{self.cpf_responsavel[3:6]}.{self.cpf_responsavel[6:9]}-**"


class ItemEstoque(db.Model):
    __tablename__ = "item_estoque"
    id = db.Column(db.Integer, primary_key=True)
    nome_item = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(40), nullable=False)
    unidade_medida = db.Column(db.String(20), nullable=False)
    quantidade_atual = db.Column(db.Integer, nullable=False)
    data_validade = db.Column(db.Date, nullable=True)
    data_entrada = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class Entrega(db.Model):
    __tablename__ = "entrega"
    id = db.Column(db.Integer, primary_key=True)
    familia_id = db.Column(db.Integer, db.ForeignKey("familia.id"), nullable=False, index=True)
    item_estoque_id = db.Column(db.Integer, db.ForeignKey("item_estoque.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    quantidade_entregue = db.Column(db.Integer, nullable=False)
    data_entrega = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    observacao = db.Column(db.String(255), nullable=True)
