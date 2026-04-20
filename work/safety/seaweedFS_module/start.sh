#!/bin/bash
# SeaweedFS Manager - Backend + Frontend 동시 실행
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== SeaweedFS Manager ==="
echo "Backend:  http://localhost:8889"
echo "Frontend: http://localhost:5173"
echo ""

# Backend
cd "$SCRIPT_DIR"
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8889 --reload &
BACKEND_PID=$!

# Frontend
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
