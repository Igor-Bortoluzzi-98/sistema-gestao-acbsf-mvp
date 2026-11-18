from datetime import datetime
from flask import Blueprint, jsonify, render_template_string, request
from .models import db, Familia, ItemEstoque, Entrega
from .services import (
    BusinessRuleError,
    cadastrar_familia,
    listar_itens_vencendo,
    registrar_entrega_fefo,
    sanitizar_texto,
)

bp = Blueprint("main", __name__)

HTML_PAINEL = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sistema de Gestão Assistencial e Estoque Comunitário - ACBSF</title>
  <style>
    :root {
      --bg: #f4f6f9;
      --surface: #ffffff;
      --text: #1a202c;
      --muted: #4a5568;
      --primary: #1b4d3e;
      --primary-text: #ffffff;
      --border: #cbd5e0;
      --badge-ok-bg: #d1fae5;
      --badge-ok-text: #065f46;
      --badge-warn-bg: #fef3c7;
      --badge-warn-text: #92400e;
      --font-scale: 1;
    }
    body.high-contrast {
      --bg: #000000;
      --surface: #000000;
      --text: #ffff00;
      --muted: #ffffff;
      --primary: #ffff00;
      --primary-text: #000000;
      --border: #ffff00;
      --badge-ok-bg: #000000;
      --badge-ok-text: #00ff00;
      --badge-warn-bg: #000000;
      --badge-warn-text: #ffff00;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      font-size: calc(16px * var(--font-scale));
      line-height: 1.5;
    }
    .a11y-bar {
      background: #111827;
      color: #ffffff;
      padding: 0.6rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
      border-bottom: 2px solid var(--border);
    }
    .a11y-bar button {
      background: #ffffff;
      color: #111827;
      border: 2px solid #ffff00;
      padding: 0.35rem 0.75rem;
      font-weight: 700;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
    }
    body.high-contrast .a11y-bar { background: #000000; color: #ffff00; }
    body.high-contrast .a11y-bar button { background: #ffff00; color: #000000; }
    header {
      background: var(--primary);
      color: var(--primary-text);
      padding: 1.25rem 1.5rem;
      border-bottom: 2px solid var(--border);
    }
    header h1 { margin: 0; font-size: 1.4rem; }
    header p { margin: 0.25rem 0 0; opacity: 0.92; font-size: 0.95rem; }
    nav.tabs {
      display: flex;
      gap: 0.5rem;
      padding: 1rem 1.5rem 0;
      max-width: 1150px;
      margin: 0 auto;
    }
    nav.tabs a {
      text-decoration: none;
      padding: 0.6rem 1.1rem;
      border: 2px solid var(--border);
      border-bottom: none;
      border-radius: 6px 6px 0 0;
      background: var(--surface);
      color: var(--text);
      font-weight: 600;
    }
    nav.tabs a.active {
      background: var(--primary);
      color: var(--primary-text);
    }
    main {
      max-width: 1150px;
      margin: 0 auto 2rem;
      padding: 1.5rem;
      background: var(--surface);
      border: 2px solid var(--border);
      border-radius: 0 6px 6px 6px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.25rem;
      margin-bottom: 1.5rem;
    }
    .card {
      border: 2px solid var(--border);
      border-radius: 6px;
      padding: 1rem;
      background: var(--surface);
    }
    .card h2 { margin-top: 0; font-size: 1.15rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
    label { display: block; font-weight: 600; margin-top: 0.65rem; }
    input, select {
      width: 100%;
      padding: 0.55rem;
      margin-top: 0.25rem;
      border: 2px solid var(--border);
      border-radius: 4px;
      background: var(--surface);
      color: var(--text);
      font-size: 1rem;
    }
    button.btn-primary {
      margin-top: 1rem;
      background: var(--primary);
      color: var(--primary-text);
      border: 2px solid var(--border);
      padding: 0.65rem 1.1rem;
      font-weight: 700;
      border-radius: 4px;
      cursor: pointer;
      width: 100%;
      font-size: 1rem;
    }
    table { width: 100%; border-collapse: collapse; margin-top: 0.75rem; }
    th, td {
      border: 1px solid var(--border);
      padding: 0.6rem;
      text-align: left;
    }
    th { background: var(--primary); color: var(--primary-text); }
    .badge {
      display: inline-block;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      font-weight: 700;
      font-size: 0.85rem;
      border: 1px solid var(--border);
    }
    .badge-ok { background: var(--badge-ok-bg); color: var(--badge-ok-text); }
    .badge-warn { background: var(--badge-warn-bg); color: var(--badge-warn-text); }
    .alert {
      padding: 0.85rem;
      border: 2px solid var(--border);
      border-radius: 4px;
      margin-bottom: 1rem;
      font-weight: 600;
      background: var(--badge-warn-bg);
      color: var(--badge-warn-text);
    }
  </style>
</head>
<body>
  <div class="a11y-bar" role="region" aria-label="Barra de Acessibilidade WCAG 2.1">
    <span><strong>Acessibilidade (ODS 2 &amp; ODS 10):</strong> <span id="a11y-status">Modo Padrão | Fonte 100%</span></span>
    <div>
      <button type="button" onclick="toggleContrast()" aria-pressed="false" id="btn-contrast">Alto Contraste</button>
      <button type="button" onclick="changeFont(0.15)">A+ Aumentar Fonte</button>
      <button type="button" onclick="changeFont(-0.15)">A- Diminuir Fonte</button>
    </div>
  </div>

  <header>
    <h1>ACBSF — Sistema de Gestão de Assistência e Estoque Comunitário</h1>
    <p>Associação Comunitária do Bairro Santa Felícia (São Carlos - SP) • Controle FEFO e Proteção LGPD</p>
  </header>

  <nav class="tabs" aria-label="Navegação Principal">
    <a href="/?aba=geral" class="{{ 'active' if aba == 'geral' else '' }}">1. Painel Geral (Famílias e Estoque FEFO)</a>
    <a href="/?aba=entregas" class="{{ 'active' if aba == 'entregas' else '' }}">2. Registro de Entregas e Carência (30 dias)</a>
  </nav>

  <main>
    {% if mensagem %}
      <div class="alert" role="alert">{{ mensagem }}</div>
    {% endif %}

    {% if aba == 'geral' %}
      <div class="grid">
        <section class="card" aria-labelledby="tit-fam">
          <h2 id="tit-fam">Cadastrar Família Beneficiária</h2>
          <form method="POST" action="/ui/familias">
            <label for="nome">Nome Completo do Responsável</label>
            <input id="nome" name="nome_responsavel" required placeholder="Ex: Maria Aparecida da Silva">
            <label for="cpf">CPF (11 dígitos - mascarado via LGPD)</label>
            <input id="cpf" name="cpf" required maxlength="14" placeholder="Ex: 32165498700">
            <label for="moradores">Quantidade de Moradores</label>
            <input id="moradores" name="qtd_moradores" type="number" min="1" value="4" required>
            <button class="btn-primary" type="submit">Salvar Cadastro da Família</button>
          </form>
        </section>

        <section class="card" aria-labelledby="tit-est">
          <h2 id="tit-est">Registrar Lote de Doação (FEFO)</h2>
          <form method="POST" action="/ui/estoque">
            <label for="prod">Produto / Cesta</label>
            <input id="prod" name="produto" required placeholder="Ex: Arroz Tipo 1 (5kg)">
            <label for="cat">Categoria</label>
            <select id="cat" name="categoria">
              <option value="Alimentos">Alimentos</option>
              <option value="Higiene">Higiene</option>
            </select>
            <label for="qtd">Quantidade (unidades)</label>
            <input id="qtd" name="quantidade" type="number" min="1" value="15" required>
            <label for="val">Data de Validade (Prioridade FEFO)</label>
            <input id="val" name="data_validade" type="date" value="2026-11-30" required>
            <button class="btn-primary" type="submit">Adicionar ao Estoque</button>
          </form>
        </section>
      </div>

      <section class="card" style="margin-bottom:1.25rem;">
        <h2>Estoque Comunitário Ordenado por Validade (Critério FEFO)</h2>
        <table>
          <thead>
            <tr>
              <th>ID Lote</th>
              <th>Produto</th>
              <th>Categoria</th>
              <th>Saldo Atual</th>
              <th>Validade</th>
              <th>Prioridade FEFO</th>
            </tr>
          </thead>
          <tbody>
            {% for item in itens %}
            <tr>
              <td>#{{ item.id }}</td>
              <td><strong>{{ item.produto }}</strong></td>
              <td>{{ item.categoria }}</td>
              <td>{{ item.quantidade_atual }} un.</td>
              <td>{{ item.data_validade.strftime('%d/%m/%Y') if item.data_validade else 'Sem validade' }}</td>
              <td>
                {% if loop.first %}
                  <span class="badge badge-warn">1º a Sair (Vencimento Próximo)</span>
                {% else %}
                  <span class="badge badge-ok">Em Estoque</span>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </section>

      <section class="card">
        <h2>Famílias Beneficiárias Cadastradas (CPF Mascarado - LGPD)</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Responsável Familiar</th>
              <th>CPF (LGPD)</th>
              <th>Moradores</th>
              <th>Situação</th>
            </tr>
          </thead>
          <tbody>
            {% for f in familias %}
            <tr>
              <td>#{{ f.id }}</td>
              <td><strong>{{ f.nome_responsavel }}</strong></td>
              <td><code>{{ f.cpf_mascarado() }}</code></td>
              <td>{{ f.qtd_moradores }} pessoas</td>
              <td><span class="badge badge-ok">Ativa / Elegível</span></td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </section>
    {% else %}
      <section class="card" style="margin-bottom:1.25rem;">
        <h2>Registrar Nova Entrega Assistencial (Baixa Automática FEFO + Carência 30 Dias)</h2>
        <form method="POST" action="/ui/entregas">
          <div class="grid" style="margin-bottom:0;">
            <div>
              <label for="fam_id">Família Beneficiária</label>
              <select id="fam_id" name="familia_id" required>
                {% for f in familias %}
                  <option value="{{ f.id }}">{{ f.nome_responsavel }} ({{ f.cpf_mascarado() }})</option>
                {% endfor %}
              </select>
            </div>
            <div>
              <label for="cat_ent">Categoria da Doação</label>
              <select id="cat_ent" name="categoria">
                <option value="Alimentos">Alimentos</option>
                <option value="Higiene">Higiene</option>
              </select>
            </div>
            <div>
              <label for="qtd_ent">Quantidade Entregue</label>
              <input id="qtd_ent" name="quantidade" type="number" min="1" value="2" required>
            </div>
          </div>
          <button class="btn-primary" type="submit">Confirmar Entrega com Validação FEFO</button>
        </form>
      </section>

      <section class="card">
        <h2>Histórico de Entregas Realizadas e Bloqueio de Duplicidade (30 dias)</h2>
        <table>
          <thead>
            <tr>
              <th>Protocolo</th>
              <th>Família</th>
              <th>Lote Baixado (FEFO)</th>
              <th>Quantidade</th>
              <th>Data/Hora</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {% for e in entregas %}
            <tr>
              <td>#ENT-{{ e.id }}</td>
              <td>{{ e.familia.nome_responsavel if e.familia else 'Família #' ~ e.familia_id }}</td>
              <td>Lote #{{ e.item_id }}</td>
              <td>{{ e.quantidade }} un.</td>
              <td>{{ e.data_entrega.strftime('%d/%m/%Y %H:%M') }}</td>
              <td><span class="badge badge-ok">Concluída (Carência Ativa 30d)</span></td>
            </tr>
            {% else %}
            <tr><td colspan="6">Nenhuma entrega registrada ainda.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </section>
    {% endif %}
  </main>

  <script>
    let scale = 1.0;
    function updateStatus() {
      const hc = document.body.classList.contains('high-contrast');
      document.getElementById('a11y-status').textContent =
        (hc ? 'Alto Contraste ATIVADO' : 'Modo Padrão') + ' | Fonte ' + Math.round(scale * 100) + '%';
    }
    function toggleContrast() {
      const active = document.body.classList.toggle('high-contrast');
      document.getElementById('btn-contrast').setAttribute('aria-pressed', active);
      updateStatus();
    }
    function changeFont(delta) {
      scale = Math.min(1.45, Math.max(0.85, +(scale + delta).toFixed(2)));
      document.documentElement.style.setProperty('--font-scale', scale);
      updateStatus();
    }
  </script>
</body>
</html>
"""


def _popular_dados_iniciais():
    if Familia.query.count() == 0:
        f1 = Familia(nome_responsavel="Maria Aparecida da Silva", cpf_hash="demo_hash_1", cpf_final="8700", qtd_moradores=4)
        f2 = Familia(nome_responsavel="José Carlos Pereira", cpf_hash="demo_hash_2", cpf_final="4321", qtd_moradores=3)
        db.session.add_all([f1, f2])
    if ItemEstoque.query.count() == 0:
        i1 = ItemEstoque(produto="Arroz Tipo 1 (5kg)", categoria="Alimentos", quantidade_atual=18, data_validade=datetime(2026, 11, 28).date())
        i2 = ItemEstoque(produto="Feijão Carioca (1kg)", categoria="Alimentos", quantidade_atual=25, data_validade=datetime(2026, 12, 15).date())
        db.session.add_all([i1, i2])
    db.session.commit()


@bp.route("/")
def index():
    _popular_dados_iniciais()
    aba = request.args.get("aba", "geral")
    mensagem = request.args.get("msg", "")
    familias = Familia.query.all()
    itens = ItemEstoque.query.order_by(ItemEstoque.data_validade.asc()).all()
    entregas = Entrega.query.order_by(Entrega.id.desc()).all()
    return render_template_string(HTML_PAINEL, aba=aba, mensagem=mensagem, familias=familias, itens=itens, entregas=entregas)


@bp.route("/ui/familias", methods=["POST"])
def ui_cadastrar_familia():
    try:
        cadastrar_familia(
            nome=request.form.get("nome_responsavel", ""),
            cpf=request.form.get("cpf", ""),
            qtd_moradores=int(request.form.get("qtd_moradores", 1)),
        )
        msg = "Família cadastrada com sucesso e CPF protegido conforme LGPD!"
    except Exception as exc:
        msg = f"Validação: {exc}"
    return index_redirect("geral", msg)


@bp.route("/ui/estoque", methods=["POST"])
def ui_cadastrar_estoque():
    val_str = request.form.get("data_validade", "")
    data_val = datetime.strptime(val_str, "%Y-%m-%d").date() if val_str else None
    item = ItemEstoque(
        produto=sanitizar_texto(request.form.get("produto", "")),
        categoria=sanitizar_texto(request.form.get("categoria", "Alimentos")),
        quantidade_atual=int(request.form.get("quantidade", 1)),
        data_validade=data_val,
    )
    db.session.add(item)
    db.session.commit()
    return index_redirect("geral", "Lote de doação registrado e ordenado pelo critério FEFO!")


@bp.route("/ui/entregas", methods=["POST"])
def ui_registrar_entrega():
    try:
        cpf_fam = ""
        familia_id = int(request.form.get("familia_id", 1))
        f = db.session.get(Familia, familia_id)
        if f:
            cpf_fam = f.cpf_responsavel
            
        registrar_entrega_fefo(
            cpf=cpf_fam,
            categoria=request.form.get("categoria", "Alimentos"),
            quantidade=int(request.form.get("quantidade", 1)),
            usuario_id=1
        )
        msg = "Entrega registrada com baixa automática FEFO! Carência de 30 dias ativada."
    except Exception as exc:
        msg = f"Bloqueio de Regra de Negócio: {exc}"
    return index_redirect("entregas", msg)


def index_redirect(aba, msg):
    from flask import redirect, url_for
    return redirect(url_for("main.index", aba=aba, msg=msg))


@bp.route("/api/familias", methods=["POST"])
def api_criar_familia():
    dados = request.get_json(silent=True) or {}
    try:
        # Suporta o formato dos testes antigos
        cpf_val = dados.get("cpf_responsavel") or dados.get("cpf", "")
        qtd_val = dados.get("qtd_integrantes") or dados.get("qtd_moradores", 1)
        
        familia = cadastrar_familia(
            nome=dados.get("nome_responsavel", ""),
            cpf=cpf_val,
            qtd_moradores=int(qtd_val),
        )
        return jsonify({
            "id": familia.id,
            "nome_responsavel": familia.nome_responsavel,
            "cpf_mascarado": familia.cpf_mascarado(),
            "qtd_moradores": familia.qtd_moradores,
        }), 201
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 400


@bp.route("/api/estoque", methods=["POST"])
def api_criar_item_estoque():
    dados = request.get_json(silent=True) or {}
    data_val = None
    if dados.get("data_validade"):
        data_val = datetime.strptime(dados["data_validade"], "%Y-%m-%d").date()

    item = ItemEstoque(
        produto=sanitizar_texto(dados.get("produto", "")),
        categoria=sanitizar_texto(dados.get("categoria", "Alimentos")),
        quantidade_atual=int(dados.get("quantidade", 0)),
        data_validade=data_val,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.id, "produto": item.produto}), 201


@bp.route("/api/estoque/vencendo", methods=["GET"])
def api_estoque_vencendo():
    dias = int(request.args.get("dias", 15))
    itens = listar_itens_vencendo(dias=dias)
    return jsonify([
        {
            "id": i.id,
            "produto": i.produto,
            "quantidade_atual": i.quantidade_atual,
            "data_validade": i.data_validade.isoformat() if i.data_validade else None,
        }
        for i in itens
    ]), 200


@bp.route("/api/entregas", methods=["POST"])
def api_criar_entrega():
    dados = request.get_json(silent=True) or {}
    try:
        entrega = registrar_entrega_fefo(
            cpf=dados.get("cpf_responsavel", ""),
            categoria=dados.get("categoria", "Alimentos"),
            quantidade=int(dados.get("quantidade", 1)),
            usuario_id=int(dados.get("usuario_id", 1))
        )
        return jsonify({
            "id": entrega.id,
            "item_id": entrega.item_id,
            "quantidade": entrega.quantidade,
        }), 201
    except Exception as exc:
        return jsonify({"erro": str(exc)}), 422
