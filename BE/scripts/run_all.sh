#!/usr/bin/env bash
# PW1 A-Z one-command demo: crawl -> AI agent -> full report export
set -euo pipefail
cd "$(dirname "$0")/.."

QUERY="${1:-christmas ornament}"
WINDOW="${2:-30d}"
SOURCES="${3:-ebay,amazon,walmart,redbubble,tiktok,demo}"

echo "═══ 1. CRAWL ($SOURCES) ═══"
curl -s -X POST http://localhost:8000/api/v1/crawl \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY\",\"sources\":\"$SOURCES\".split(','),\"max_items\":12}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {r[\"source\"]}: {r[\"status\"]} ({r[\"products\"]} products) {r[\"error\"][:60]}') for r in d['results']]"

echo ""
echo "═══ 2. AI AGENT ANALYZE ═══"
curl -s -X POST http://localhost:8000/api/v1/agent/analyze \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY\",\"window\":\"$WINDOW\",\"data_source\":\"MARKET_SIGNALS\",\"limit\":10,\"deep\":true}" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'  raw records read: {d[\"raw_records_read\"]} | sources: {\",\".join(d[\"sources_used\"])}')
print('  top keywords:')
for k in d['top_keywords'][:5]:
    print(f'    {k[\"keyword\"][:45]:47s} D={k[\"demand\"]:>5} G={k[\"growth\"]:>5} | {k[\"recommended_product\"][:40]}')
print('  top products (revenue):')
for p in d['top_products_revenue'][:3]:
    print(f'    {p[\"title\"][:42]:44s} {p[\"source\"]:10s} \${p[\"revenue\"]:>10,.2f} qty={p[\"quantity\"]}')
print('  R&D recommendations:')
for r in d['rd_recommendations'][:3]:
    print(f'    #{r[\"rank\"]} {r[\"product\"][:50]:52s} score={r[\"opportunity_score\"]}')
print('  agent trace:')
for t in d['agent_trace']:
    print(f'    - {t}')
"

echo ""
echo "═══ 3. EXPORT REPORTS ═══"
SLUG=$(echo "$QUERY" | tr ' ' '_')
for fmt in xlsx pdf md json; do
  curl -s -o "data/exports/final_${SLUG}.${fmt}" \
    "http://localhost:8000/api/v1/agent/reports/$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY")/export?format=$fmt"
  echo "  data/exports/final_${SLUG}.${fmt} ($(wc -c < "data/exports/final_${SLUG}.${fmt" | tr -d ' ') bytes)"
done

echo ""
echo "✅ A-Z COMPLETE - reports in data/exports/"
