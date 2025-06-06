# a, b = map(int, input().split())

        
# from sys import stdin

# with open('f.txt', encoding="UTF-8") as file_open:
#     for line in file_open:
#         print(line.strip('\n')) 


# def gcd(x, y):
#     while x > 0 and y > 0:
#         if x > y:
#             x %= y
#         else:
#             y %= x
#     return max(x,y)

# x, y = int(input()), int(input())
# print(gcd(x,y))


# from sys import stdin
# import json

# data = [line.strip() for line in stdin]
# print(data)
# print({line.split(' == ')[0]: line.split(' == ')[1] for line in data[1:]})
# D = {line.split(' == ')[0]: line.split(' == ')[1] for line in data[1:]}
# with open(data[0], encoding='UTF-8') as f:
#     records = json.load(f)
# records.update(D)
# if len(data) > 1:
#     with open(data[0], 'w', encoding='UTF-8') as f:
#         json.dump(records, f, ensure_ascii=False, indent=4, sort_keys=True)



# LITER = {
#     'А': 'A', 'Б': 'B', 'В': 'V',
#     'Г': 'G', 'Д': 'D', 'Е': 'E',
#     'Ё': 'E', 'Ж': 'ZH', 'З': 'Z',
#     'И': 'I', 'Й': 'I', 'К': 'K',
#     'Л': 'L', 'М': 'M', 'Н': 'N',
#     'О': 'O', 'П': 'P', 'Р': 'R',
#     'С': 'S', 'Т': 'T', 'У': 'U',
#     'Ф': 'F', 'Х': 'KH', 'Ц': 'TC',
#     'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHCH',
#     'Ы': 'Y', 'Э': 'E', 'Ю': 'IU',
#     'Я': 'IA', 'Ь': '', 'Ъ': '',
# }

# with open('cyrillic.txt', encoding='UTF-8') as f:
#     with open('transliteration.txt', 'w', encoding='UTF-8') as wr:
#         for word in f:
#             word = word.strip()  # Убираем перенос строки
#             for letter in word:
#                 if letter.upper() in LITER:
#                     translit_letter = LITER[letter.upper()]
#                     if letter.islower():
#                         translit_letter = translit_letter.lower()
#                 else:
#                     translit_letter = letter
                
#                 wr.write(translit_letter)
#             wr.write("\n")  # Добавляем перенос вручную






    







