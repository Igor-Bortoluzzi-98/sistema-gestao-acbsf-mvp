# Sistema Web de Gestão de Assistência e Estoque Comunitário - ACBSF (MVP)

Aplicação web responsiva desenvolvida em **Python 3.12** e **Flask 3.0** (Arquitetura Monolítica em 3 Camadas - MVC) para a **Associação Comunitária do Bairro Santa Felícia (ACBSF)**, em São Carlos - SP.

## Objetivo e Alinhamento Social (ODS)
Substituir controles manuais em cadernos por uma gestão unificada de famílias assistidas e lotes de doações, conectada ao **ODS 2 (Fome Zero - Meta 2.1)** e ao **ODS 12 (Consumo e Produção Responsáveis - Meta 12.3)**:
- **Bloqueio automático de duplicidade:** impede nova entrega da mesma categoria para um mesmo CPF dentro da carência de 30 dias (RF03).
- **Priorização FEFO (*First Expired, First Out*):** ordena e abate automaticamente lotes com data de validade mais próxima (RF02 / RF04).
- **Segurança e Acessibilidade:** hash unidirecional `PBKDF2-HMAC-SHA256` (RNF01), proteção OWASP Top 10 / mascaramento parcial de CPF (RNF02) e interface acessível WCAG 2.1 AA (RNF04).

## Estrutura do Projeto (MVC)
```text
├── app/
│   ├── __init__.py       # Configuração Flask e banco de dados
│   ├── models.py         # Camada Model (Usuario, Familia, ItemEstoque, Entrega)
│   ├── services.py       # Camada Service (Regras de negócio: carência 30 dias e FEFO)
│   └── routes.py         # Camada Controller (Rotas HTTP, validação e segurança)
├── tests/
│   └── test_mvp.py       # Testes unitários e de integração (pytest)
├── .github/workflows/
│   └── ci.yml            # Pipeline de Integração Contínua (GitHub Actions)
├── .env.example          # Modelo de variáveis de ambiente
└── requirements.txt      # Dependências fixadas
