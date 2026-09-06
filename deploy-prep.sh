#!/usr/bin/env bash
# Build a clean, publishable copy of the site into ./_site
#
#   ./deploy-prep.sh https://your-site-url.example
#
# Everything the public needs goes in. Build scripts, the Python virtualenv, the
# raw research notes and the agent brief stay out.
set -euo pipefail
cd "$(dirname "$0")"

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "usage: ./deploy-prep.sh https://your-site-url.example" >&2
  exit 1
fi
URL="${URL%/}"

rm -rf _site && mkdir -p _site

# --- the site itself ---
cp -- *.html _site/
cp -r css js data assets _site/
cp .nojekyll _site/ 2>/dev/null || true

# --- publish the evidence, because the site's whole claim is that it is sourced ---
mkdir -p _site/research
cp research/SCHEMA.md research/batch-*.json research/gapfill.json _site/research/ 2>/dev/null || true
cp "Sec Tools - expanded.xlsx" _site/ 2>/dev/null || true
cp README.md _site/ 2>/dev/null || true

# --- stamp the real URL into the crawler files and canonical tags ---
cat > _site/robots.txt <<EOF
User-agent: *
Allow: /

Sitemap: $URL/sitemap.xml
EOF

{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  for p in index quiz compare glossary about; do
    echo "  <url><loc>$URL/$p.html</loc><changefreq>monthly</changefreq></url>"
  done
  echo '</urlset>'
} > _site/sitemap.xml

for f in _site/*.html; do
  base="$(basename "$f")"
  python3 - "$f" "$URL/$base" "$URL" <<'PY'
import sys, re
path, canon, site = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path).read()
if 'rel="canonical"' not in s:
    s = s.replace('<link rel="stylesheet"',
                  f'<link rel="canonical" href="{canon}">\n<link rel="stylesheet"', 1)
if 'og:url' not in s:
    s = s.replace('<meta property="og:type"',
                  f'<meta property="og:url" content="{canon}">\n<meta property="og:type"', 1)
open(path, "w").write(s)
PY
done

echo "built _site/ for $URL"
du -sh _site | sed 's/^/  /'
find _site -type f | wc -l | xargs echo "  files:"
