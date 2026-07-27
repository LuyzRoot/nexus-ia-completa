#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Instala plugin por upload via API ou por cópia local
ENV_FILE=".env"
API_URL="${API_URL:-http://localhost:8000/api/v1/admin/plugins/upload}"
PLUGINS_DIR="plugins/installed"

usage(){
  cat <<EOF
install_plugin.sh --zip plugin.zip
install_plugin.sh --dir /path/to/plugin_dir

Options:
  --zip FILE     envia zip para a API de admin (requer endpoint /api/v1/admin/plugins/upload)
  --dir PATH     copia diretório para plugins/installed/
EOF
}

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

if [[ $# -lt 2 ]]; then
  usage; exit 1
fi

case "$1" in
  --zip)
    ZIP="$2"
    if [[ ! -f "$ZIP" ]]; then
      echo "Zip não encontrado: $ZIP"; exit 1
    fi
    echo "Uploading $ZIP to $API_URL"
    if command -v curl >/dev/null 2>&1; then
      curl -F "file=@${ZIP}" "$API_URL"
    else
      echo "curl not available"
      exit 1
    fi
    ;;
  --dir)
    SRC="$2"
    if [[ ! -d "$SRC" ]]; then
      echo "Diretório não encontrado: $SRC"; exit 1
    fi
    BASENAME=$(basename "$SRC")
    DEST="$PLUGINS_DIR/$BASENAME"
    mkdir -p "$PLUGINS_DIR"
    if [[ -d "$DEST" ]]; then
      echo "Plugin $BASENAME já existe em $DEST; removendo (sobrescrever)"
      rm -rf "$DEST"
    fi
    cp -r "$SRC" "$DEST"
    echo "Plugin copiado para $DEST"
    ;;
  *)
    usage; exit 1
    ;;
esac