# Auth (NEXUS)

Arquivos:
- routes.py -> endpoints: register, login, me
- deps.py   -> get_current_user, require_admin
- schemas.py -> Pydantic models para token e usuário

Integração:
1. Inclua o router no app/main.py (ou app.routes) para ativar os endpoints:
   from app.auth.routes import router as auth_router
   app.include_router(auth_router)

2. Se já possui um endpoint de login/register (ex.: app/api/auth.py), prefira manter apenas um para evitar duplicidade de rotas.

Observações:
- A criação e validação de tokens usa funções em `app.config.security` (create_access_token e decode_access_token).
- Ajuste oauth2_scheme.tokenUrl em deps.py caso mude a rota de login.
- Proteja endpoints administrativos usando `Depends(require_admin)`.