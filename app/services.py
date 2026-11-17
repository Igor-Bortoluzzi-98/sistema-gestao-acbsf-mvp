from datetime import datetime, timedelta, timezone
from app import db
from app.models import Familia, ItemEstoque, Entrega


class RegraNegocioError(ValueError):
    pass


def validar_cpf_numerico(cpf: str) -> str:
    digitos = "".join(ch for ch in (cpf or "") if ch.isdigit())
    if len(digitos) != 11 or len(set(digitos)) == 1:
        raise RegraNegocioError("CPF inválido: informe 11 dígitos numéricos válidos.")
    return digitos


def listar_estoque_fefo():
    return (
        ItemEstoque.query.filter(ItemEstoque.quantidade_atual > 0)
        .order_by(ItemEstoque.data_validade.asc().nullslast())
        .all()
    )


def verificar_elegibilidade_mensal(familia_id: int, categoria: str, dias_carencia: int = 30):
    limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=dias_carencia)
    ultima = (
        db.session.query(Entrega)
        .join(ItemEstoque, Entrega.item_estoque_id == ItemEstoque.id)
        .filter(
            Entrega.familia_id == familia_id,
            ItemEstoque.categoria == categoria,
            Entrega.data_entrega >= limite,
        )
        .order_by(Entrega.data_entrega.desc())
        .first()
    )
    if ultima:
        proxima = ultima.data_entrega + timedelta(days=dias_carencia)
        raise RegraNegocioError(
            f"Bloqueio de duplicidade: família já retirou item desta categoria em "
            f"{ultima.data_entrega.strftime('%d/%m/%Y')}. "
            f"Próxima liberação em {proxima.strftime('%d/%m/%Y')}."
        )
    return True


def registrar_entrega_fefo(cpf: str, categoria: str, quantidade: int, usuario_id: int):
    if quantidade <= 0:
        raise RegraNegocioError("A quantidade entregue deve ser maior que zero.")

    cpf_limpo = validar_cpf_numerico(cpf)
    familia = Familia.query.filter_by(cpf_responsavel=cpf_limpo, status="ativo").first()
    if not familia:
        raise RegraNegocioError("Família não encontrada ou inativa para o CPF informado.")

    verificar_elegibilidade_mensal(familia.id, categoria)

    lote = (
        ItemEstoque.query.filter(
            ItemEstoque.categoria == categoria,
            ItemEstoque.quantidade_atual >= quantidade,
        )
        .order_by(ItemEstoque.data_validade.asc().nullslast())
        .first()
    )
    if not lote:
        raise RegraNegocioError("Saldo insuficiente em estoque para a categoria solicitada.")

    lote.quantidade_atual -= quantidade
    entrega = Entrega(
        familia_id=familia.id,
        item_estoque_id=lote.id,
        usuario_id=usuario_id,
        quantidade_entregue=quantidade,
    )
    db.session.add(entrega)
    db.session.commit()
    return entrega, lote

def listar_itens_vencendo(dias_alerta: int = 10):
    from datetime import date, timedelta
    limite = date.today() + timedelta(days=dias_alerta)
    return (
        ItemEstoque.query.filter(
            ItemEstoque.quantidade_atual > 0,
            ItemEstoque.data_validade.isnot(None),
            ItemEstoque.data_validade <= limite,
        )
        .order_by(ItemEstoque.data_validade.asc())
        .all()
    )
