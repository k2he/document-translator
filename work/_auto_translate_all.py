import json
import re
import time
from pathlib import Path

import requests

in_path = Path('work/extracted_segments.json')
out_path = Path('work/translated_segments.json')
segments = json.loads(in_path.read_text(encoding='utf-8'))

cjk_re = re.compile(r'[\u4e00-\u9fff]')

unique_sources = []
seen = set()
for seg in segments:
    src = seg['source']
    if src not in seen:
        seen.add(src)
        unique_sources.append(src)

translation_map = {}


def translate_text(text: str) -> str:
    url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx',
        'sl': 'zh-CN',
        'tl': 'en',
        'dt': 't',
        'q': text,
    }
    for attempt in range(5):
        try:
            resp = requests.get(url, params=params, timeout=20)
            if resp.status_code != 200:
                raise RuntimeError(f'status={resp.status_code}')
            data = resp.json()
            if not data or not data[0]:
                return text
            translated = ''.join(part[0] for part in data[0] if part and part[0])
            translated = translated.strip()
            return translated or text
        except Exception:
            time.sleep(0.8 * (attempt + 1))
    return text

needs_translation = []
for src in unique_sources:
    if cjk_re.search(src):
        needs_translation.append(src)
    else:
        translation_map[src] = src

total = len(needs_translation)
for idx, src in enumerate(needs_translation, start=1):
    translation_map[src] = translate_text(src)
    if idx % 50 == 0 or idx == total:
        print(f'translated_unique {idx}/{total}')

out = []
for seg in segments:
    src = seg['source']
    out.append({
        'id': seg['id'],
        'source': src,
        'translation': translation_map.get(src, src),
    })

out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

remaining = sum(1 for item in out if cjk_re.search(item['translation']))
print('written', out_path)
print('segments', len(out))
print('unique_sources', len(unique_sources))
print('remaining_chinese_in_translation', remaining)
