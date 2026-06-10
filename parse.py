import re
html=open('naver_form.html', encoding='utf-8').read()
categories = re.findall(r'<span class="SelectGroup_item_label[^>]*>(.*?)</span>', html)
print(categories)
