import re
html = open('C:\\Users\\greyi\\.gemini\\antigravity-ide\\brain\\4a36a366-c0ad-42ad-a835-2d07eb3e1dc8\\.system_generated\\steps\\3421\\content.md', encoding='utf-8').read()
text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL|re.IGNORECASE)
text = re.sub(r'<svg[^>]*>.*?</svg>', '', text, flags=re.DOTALL|re.IGNORECASE)
text = re.sub(r'<[^>]+>', ' ', text)
text = re.sub(r'\s+', ' ', text)
open('text.txt', 'w', encoding='utf-8').write(text)
