#!/usr/bin/env sh
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "错误: 未找到 $ENV_FILE"
  echo "请执行: cp .env.example .env 并填入 DEEPSEEK_API_KEY"
  exit 1
fi

# shellcheck disable=SC1090
. "$ENV_FILE"

if [ -z "${DEEPSEEK_API_KEY:-}" ] || [ "$DEEPSEEK_API_KEY" = "your_api_key_here" ]; then
  echo "错误: .env 中 DEEPSEEK_API_KEY 未配置"
  exit 1
fi

echo "OK: .env 已就绪 (APP_PORT=${APP_PORT:-35001})"
