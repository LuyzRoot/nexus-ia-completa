# Guia de Setup Completo — nexus-ia-completa

Este arquivo reúne instruções práticas e um script automatizado para deixar o repositório pronto e funcionando sem erros (na medida do possível). Tudo está separado em seções claras: preparação do ambiente Python, dependências, configuração de variáveis de ambiente, frontend, e como iniciar o projeto.

IMPORTANTE: o script automatiza passos comuns, mas você deve revisar e preencher o arquivo `.env` com suas chaves e credenciais antes de rodar em produção.

1) Requisitos mínimos
- Python 3.8+ (recomendado 3.10+)
- Git
- curl/wget
- Node.js + npm/yarn (se for usar a pasta frontend)

2) Passos rápidos (execução manual)
- Clonar o repositório:
  git clone https://github.com/LuyzRoot/nexus-ia-completa.git
  cd nexus-ia-completa

- Criar e ativar ambiente virtual (Linux/macOS):
  python3 -m venv .venv
  source .venv/bin/activate

- Atualizar pip e instalar dependências:
  pip install --upgrade pip
  pip install -r requirements.txt

- Criar o arquivo .env (se não existir) a partir do exemplo e editar com suas chaves:
  cp .env.example .env
  # editar .env com suas variáveis (OPENAI_KEY, DATABASE_URL, etc)

- Se houver backend que precise rodar migrations, executar as migrations apropriadas (ver README específico da pasta database ou scripts).

- Frontend (se usar):
  cd frontend
  # se houver package.json
  npm install
  npm run dev  # ou npm run build && npm start

3) Uso do script automatizado
- Torne o script executável e rode:
  chmod +x scripts/setup_complete.sh
  ./scripts/setup_complete.sh

Por padrão, o script agora RODA MIGRATIONS AUTOMATICAMENTE (alembic upgrade head) usando um banco SQLite local dev.db, a menos que o .env contenha uma DATABASE_URL diferente. Se preferir non‑interactive behavior diferente, use as flags:
- Para desabilitar migrations automáticos: ./scripts/setup_complete.sh --no-migrate
- Para forçar a execução explícita: ./scripts/setup_complete.sh --migrate

O script irá:
- checar python3
- criar .venv (se não existir)
- atualizar pip e instalar requirements.txt
- criar .env a partir de .env.example se necessário
- instalar alembic no venv e rodar `alembic upgrade head` (cria/atualiza dev.db em SQLite)
- exibir as próximas instruções para rodar o projeto

4) Banco de desenvolvimento (SQLite)
- Por padrão em dev, o projeto usará sqlite:///dev.db se DATABASE_URL não estiver definido.
- Isso cria um arquivo dev.db na raiz do repositório para facilitar desenvolvimento local.

5) Problemas comuns e como resolver
- Erro de compilação de pacote nativo: instale build-essential e libssl, python3-dev (Linux).
  Exemplo Debian/Ubuntu:
  sudo apt update && sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

- Erros de versão de pip: rode pip install --upgrade pip setuptools wheel

6) Depois que tudo estiver pronto
- Ative o venv: source .venv/bin/activate
- Execute o backend principal (ex.): python nexus_main.py
- Se houver comando específico no README, siga-o; este guia é genérico e cobre preparação comum.

7) Arquivos criados/atualizados
- scripts/setup_complete.sh  — script automatizado para setup (migrations automáticas por padrão)
- alembic/ (env.py) e alembic.ini — configuração Alembic para usar SQLite dev.db por padrão
- SETUP_COMPLETE.md        — este arquivo (existe agora)

Se quiser, eu posso também adaptar o script para rodar migrations apenas em ambientes específicos, criar um docker-compose pronto, ou gerar uma migration inicial automaticamente; me diga qual opção prefere e eu atualizo automaticamente.
