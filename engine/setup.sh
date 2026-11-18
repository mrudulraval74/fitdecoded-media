#!/bin/sh
# Fetch the MIT-licensed 3D emoji images used by the renderer into engine/icons
set -e
cd "$(dirname "$0")"
[ -d icons ] && [ "$(ls icons | wc -l)" -gt 1000 ] && exit 0
tmp=$(mktemp -d)
(cd "$tmp" && npm pack @lobehub/fluent-emoji-3d@1.1.0 --silent >/dev/null && tar xzf *.tgz)
mkdir -p icons && cp "$tmp"/package/assets/*.webp icons/ && rm -rf "$tmp"
echo "icons ready: $(ls icons | wc -l)"
