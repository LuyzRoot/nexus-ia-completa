# Plugins

O NEXUS possui um subsistema de plugins que permite estender funcionalidades.

Localização
- Diretório: `plugins/installed/`
- Arquivos: cada plugin deve ser um package Python importável como `plugins.installed.<plugin_folder>`

Contrato do plugin
- `plugin.json` (opcional): metadados (id, name, version, author, enabled)
- `__init__.py` ou módulo com `def setup(api):` que recebe `PluginAPI` do host
- Opcional: `def teardown(api):` para limpeza

PluginAPI (apenas resumo)
- `add_skill(name, handler)` — registra um skill no host
- `add_router(router)` — registra um FastAPI router no app principal

Gestão
- Instalação via admin API: `POST /api/v1/admin/plugins/upload` (zip)
- Habilitar / Desabilitar: `POST /api/v1/admin/plugins/{id}/enable` ou `/disable`
- Remover: `DELETE /api/v1/admin/plugins/{id}`

Segurança
- Apenas admins devem poder instalar/habilitar plugins.
- Plugins executados `in-process` são tão confiáveis quanto o código do plugin — use sandbox (opcional) ao carregar plugins não confiáveis.