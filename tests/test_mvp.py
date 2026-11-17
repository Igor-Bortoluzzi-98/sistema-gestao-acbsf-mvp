from datetime import date, timedelta
import pytest
from app import create_app, db
from app.models import Usuario, Familia, ItemEstoque


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        u = Usuario(nome_completo="Roberto Sampaio", email="roberto@acbsf.org", perfil="gestor")
        u.definir_senha("SenhaForte123")
        db.session.add(u)
        db.session.commit()
    with app.test_client() as c:
        yield c


def test_hash_senha_seguro(client):
    with client.application.app_context():
        u = Usuario.query.filter_by(email="roberto@acbsf.org").first()
        assert u.senha_hash != "SenhaForte123"
        assert u.senha_hash.startswith("pbkdf2:sha256:")
        assert u.verificar_senha("SenhaForte123") is True


def test_cadastro_familia_e_bloqueio_cpf_duplicado(client):
    payload = {
        "nome_responsavel": "Maria Aparecida Souza",
        "cpf_responsavel": "12345678909",
        "endereco_resumido": "Rua das Flores, 100 - Santa Felícia",
        "qtd_integrantes": 4,
    }
    r1 = client.post("/api/familias", json=payload)
    assert r1.status_code == 201
    assert r1.get_json()["cpf_mascarado"] == "***.456.789-**"

    r2 = client.post("/api/familias", json=payload)
    assert r2.status_code == 409


def test_entrega_prioriza_fefo_e_bloqueia_duplicidade_mensal(client):
    with client.application.app_context():
        fam = Familia(
            nome_responsavel="João Silva",
            cpf_responsavel="98765432100",
            endereco_resumido="Av. Trabalhador São-Carlense, 50",
            qtd_integrantes=3,
        )
        lote_longe = ItemEstoque(
            nome_item="Cesta Básica Lote B",
            categoria="cesta_basica",
            unidade_medida="unidade",
            quantidade_atual=10,
            data_validade=date.today() + timedelta(days=60),
        )
        lote_perto = ItemEstoque(
            nome_item="Cesta Básica Lote A",
            categoria="cesta_basica",
            unidade_medida="unidade",
            quantidade_atual=5,
            data_validade=date.today() + timedelta(days=7),
        )
        db.session.add_all([fam, lote_longe, lote_perto])
        db.session.commit()
        id_lote_perto = lote_perto.id

    res1 = client.post(
        "/api/entregas",
        json={"cpf_responsavel": "98765432100", "categoria": "cesta_basica", "quantidade": 1, "usuario_id": 1},
    )
    assert res1.status_code == 201
    dados = res1.get_json()
    assert dados["lote_utilizado_id"] == id_lote_perto
    assert dados["saldo_restante"] == 4

    res2 = client.post(
        "/api/entregas",
        json={"cpf_responsavel": "98765432100", "categoria": "cesta_basica", "quantidade": 1, "usuario_id": 1},
    )
    assert res2.status_code == 422
    assert "Bloqueio de duplicidade" in res2.get_json()["erro"]
