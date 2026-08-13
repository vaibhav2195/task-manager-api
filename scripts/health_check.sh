#!/usr/bin/env bash
set -euo pipefail

# Configuration defaults
BASE_URL="${1:-http://localhost:8000}"
HEALTH_ENDPOINT="${BASE_URL}/health"
MAX_RETRIES=5
RETRY_INTERVAL=2

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} Testing API Health Endpoint at: ${HEALTH_ENDPOINT}"

attempt=1
while [ $attempt -le $MAX_RETRIES ]; do
    echo -n -e "${YELLOW}[TRY ${attempt}/${MAX_RETRIES}]${NC} Sending GET request to ${HEALTH_ENDPOINT}... "
    
    RESPONSE=$(curl -s -w "\n%{http_code}" --max-time 5 "${HEALTH_ENDPOINT}" || echo "FAILED")
    
    HTTP_BODY=$(echo "$RESPONSE" | head -n -1)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}HTTP 200 OK${NC}"
        
        # Verify JSON content with grep
        if echo "$HTTP_BODY" | grep -q '"status":\s*"ok"' || echo "$HTTP_BODY" | grep -q '"status":"ok"'; then
            echo -e "${GREEN}[SUCCESS]${NC} Health Check PASSED!"
            echo -e "Payload: $HTTP_BODY"
            exit 0
        else
            echo -e "${RED}[FAIL]${NC} Status code 200 but payload did not contain '\"status\": \"ok\"'."
            echo -e "Payload: $HTTP_BODY"
        fi
    else
        echo -e "${RED}HTTP ${HTTP_CODE}${NC}"
    fi

    attempt=$((attempt + 1))
    if [ $attempt -le $MAX_RETRIES ]; then
        sleep $RETRY_INTERVAL
    fi
done

echo -e "${RED}[ERROR]${NC} Health Check FAILED after ${MAX_RETRIES} attempts."
exit 1
