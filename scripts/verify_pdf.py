import pdfplumber

p = pdfplumber.open(r'D:\Database_Design_Document.pdf')
print('=== PDF Page Analysis ===')
print('Total pages:', len(p.pages))
for i, page in enumerate(p.pages):
    words = page.extract_words()
    max_b = max(w['bottom'] for w in words) if words else 0
    print(f'Page {i+1}: text words={len(words)}, max_bottom={max_b:.1f} / {page.height} ({max_b/page.height*100:.1f}% filled)')
p.close()
