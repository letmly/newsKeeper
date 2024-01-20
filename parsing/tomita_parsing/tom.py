import re

textfile = 'verypeople.txt'
with open(textfile, 'r', encoding='utf-8') as f:
    text = f.read()

# удаление пустых строк
text = "\n".join([line for line in text.split("\n") if line.strip()])

# удаление цифр и знаков пунктуации
text = re.sub(r"[^а-яА-Я\s]+", "", text)
text = "\n".join([line.lstrip() for line in text.split("\n")])

essentials = 'essentials.txt'
with open(essentials, 'w', encoding='utf-8') as f:
        f.write(text)
