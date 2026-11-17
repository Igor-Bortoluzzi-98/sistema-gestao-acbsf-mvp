from flask import Blueprint, jsonify, request
from app import db
from app.models import Familia
from app.services import (
    RegraNegocioError,
    listar_estoque_fefo,
    registrar_entrega_fefo,
    validar_cpf_numerico,
)

bp = Blueprint("main", __name__)


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "projeto": "ACBSF-MVP"}), 200


@bp.route("/api/familias", methods=["POST"])
def cadastrar_familia():
    dados = request.get_json(silent=True) or {}
    try:
        cpf = validar_cpf_numerico(dados.get("cpf_responsavel", ""))
        if Familia.query.filter_by(cpf_responsavel=cpf).first():
            return jsonify({"erro": "CPF já cadastrado no sistema."}), 409

        familia = Familia(
            nome_responsavel=dados.get("nome_responsavel", "").strip(),
            cpf_responsavel=cpf,
            endereco_resumido=dados.get("endereco_resumido", "").strip(),
            qtd_integrantes=int(dados.get("qtd_integrantes", 1)),
        )
        db.session.add(familia)
        db.session.commit()
        return jsonify({"id": familia.id, "cpf_mascarado": familia.cpf_mascarado()}), 201
    except (RegraNegocioError, ValueError) as exc:
        return jsonify({"erro": str(exc)}), 400


@bp.route("/api/estoque", methods=["GET"])
def consultar_estoque():
    itens = listar_estoque_fefo()
    return jsonify(
        [
            {
                "id": i.id,
                "nome_item": i.nome_item,
                "categoria": i.categoria,
                "quantidade_atual": i.quantidade_atual,
                "data_validade": i.data_validade.isoformat() if i.data_validade else None,
            }
            for i in itens
        ]
    ), 200


@bp.route("/api/entregas", methods=["POST"])
def criar_entrega():
    dados = request.get_json(silent=True) or {}
    try:
        entrega, lote = registrar_entrega_fefo(
            cpf=dados.get("cpf_responsavel", ""),
            categoria=dados.get("categoria", ""),
            quantidade=int(dados.get("quantidade", 1)),
            usuario_id=int(dados.get("usuario_id", 1)),
        )
        return jsonify(
            {
                "entrega_id": entrega.id,
                "lote_utilizado_id": lote.id,
                "saldo_restante": lote.quantidade_atual,
            }
        ), 201
    except RegraNegocioError as exc:
        return jsonify({"erro": str(exc)}), 422
