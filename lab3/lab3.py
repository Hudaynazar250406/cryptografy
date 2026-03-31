from collections import OrderedDict
import numpy as np
import sys


def decryption_format(dec_text):
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace('прб', ' ')
    result = dec_text[0].upper() + dec_text[1:]
    result_list = list(result)

    for i in range(len(result_list) - 3):
        if result_list[i] == ".":
            result_list[i + 2] = result_list[i + 2].upper()

    result = ""
    for char in result_list:
        result += char

    return result


def generate_table(keyword):
    start_alphabet = "абвгдежзиклмнопрстуфхцчшщъыэюя"
    keyword, count = "".join(keyword.split()), 0
    string_table = "".join(OrderedDict.fromkeys(keyword + start_alphabet))
    table = [[0] * 6 for _ in range(5)]
    for i in range(5):
        for j in range(6):
            table[i][j] = string_table[count]
            count += 1
    return table


def find_index(array, element):
    flat_array = [item for sublist in array for item in sublist]
    try:
        return flat_array.index(element) // len(array[0]), flat_array.index(element) % len(array[0])
    except ValueError:
        return None


def prepare_text_for_playfair(text):
    # подготовка текста: разбивка на пары, вставка "ф" при одинаковых буквах, добивка до чётной длины
    res = ""
    i = 0
    while i < len(text):
        f = text[i]
        if i + 1 < len(text):
            s = text[i + 1]
            if f == s:
                res += f + "ф"
                i += 1
            else:
                res += f + s
                i += 2
        else:
            res += f + "ф"
            i += 1
    return res


def Playfair_cipher(operation, text, answer=""):

    key: str = str(input('Введите ключевое слово (без повторяющихся букв): '))
    table = generate_table(key)

    if operation == 1:  # шифрование
        # подготовка текста отдельно, потом шифрование по готовым парам
        text = prepare_text_for_playfair(text)

        for i in range(0, len(text), 2):
            f_let = text[i]
            s_let = text[i + 1]

            f_let_i, f_let_j = find_index(table, f_let)[0], find_index(table, f_let)[1]
            s_let_i, s_let_j = find_index(table, s_let)[0], find_index(table, s_let)[1]

            if f_let_i == s_let_i:  # если в таблице в одной строке
                answer += table[f_let_i][(f_let_j + 1) % 6]
                answer += table[s_let_i][(s_let_j + 1) % 6]
                continue

            if f_let_j == s_let_j:  # если в таблице в одном столбце
                answer += table[(f_let_i + 1) % 5][f_let_j]
                answer += table[(s_let_i + 1) % 5][s_let_j]
                continue

            if f_let_i != s_let_i and f_let_j != s_let_j:
                answer += table[f_let_i][s_let_j]
                answer += table[s_let_i][f_let_j]
                continue

        print("Зашифрованный текст: ", ' '.join(answer[i: i + 5] for i in range(0, len(answer), 5)))

    if operation == 2:  # расшифрование

        for i in range(0, len(text) - 1, 2):

            f_let = text[i]
            s_let = text[i + 1]

            f_let_i, f_let_j = find_index(table, f_let)[0], find_index(table, f_let)[1]
            s_let_i, s_let_j = find_index(table, s_let)[0], find_index(table, s_let)[1]

            if f_let_i == s_let_i:  # если в таблице в одной строке
                answer += table[f_let_i][(f_let_j - 1) % 6]
                answer += table[s_let_i][(s_let_j - 1) % 6]
                continue

            if f_let_j == s_let_j:  # если в таблице в одном столбце
                answer += table[(f_let_i - 1) % 5][f_let_j]
                answer += table[(s_let_i - 1) % 5][s_let_j]
                continue

            if f_let_i != s_let_i and f_let_j != s_let_j:
                answer += table[f_let_i][s_let_j]
                answer += table[s_let_i][f_let_j]
                continue

        result = decryption_format(answer)

        print("Расшифрованный текст: ", result, end='')


def matrix_cipher(operation, text, answer=""):

    alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    key_matrix = np.zeros((3, 3))

    print("Введите матрицу 3x3 (каждую строку с новой строки, элементы через пробел):")
    for rows in range(3):
        row = input().split()
        for cols in range(3):
            key_matrix[rows, cols] = int(row[cols])

    if np.linalg.det(key_matrix) != 0:

        if operation == 1:  # шифрование

            text += "ф" * ((3 - len(text) % 3) % 3)

            for i in range(0, len(text), 3):

                cur_matrix = np.zeros((3, 1))

                for j in range(3):
                    cur_matrix[j, 0] = alphabet.index(text[j + i]) + 1

                l_matrix = np.matmul(key_matrix, cur_matrix)

                for k in range(3):
                    answer += str(int(l_matrix[k, 0])) + " "

            print("Зашифрованный текст: ", answer)

        else:  # расшифрование

            ciphertext, enc_text = text.split(" "), []
            key_matrix = np.linalg.inv(key_matrix)

            for i in range(0, len(ciphertext), 3):

                cur_matrix = np.zeros((3, 1))

                for j in range(3):
                    cur_matrix[j, 0] = int(ciphertext[j + i])

                l_matrix = np.matmul(key_matrix, cur_matrix)

                for pos in range(3):
                    enc_text.append(round(l_matrix[pos, 0]) - 1)

            for i in range(len(enc_text)):
                answer += alphabet[int(enc_text[i])]

            answer = decryption_format(answer)
            while answer[-1] == "ф":
                answer = answer[:-1]

            print("Расшифрованный текст: ", answer, end='')

    else:
        print("Ошибка! Определитель матрицы равен 0.")
        exit()


while True:

    print("""Выберите шифр:
             1. Шифр Плейфера
             2. Матричный шифр
             3. Выход
         """)
    select: int = int(input("Ваш выбор: "))
    if select == 3:
        sys.exit()

    if select not in [1, 2, 3]:
        print("Неверный выбор! Попробуйте снова.")
        continue

    print("""Выберите действие:
                1. Шифрование
                2. Расшифрование""")
    operation: int = int(input("Ваш выбор: "))
    if operation not in [1, 2]:
        print("Неверный выбор! Попробуйте снова.")
        continue

    text: str = str(input('Введите текст: '))
    print()

    if operation == 1:
        for i in range(len(text)):

            if text.find('.') != -1:
                index = text.find('.')
                str1_split1 = text[:index]
                str1_split2 = text[index + 1:]
                text = str1_split1 + 'тчк' + str1_split2

            if text.find(',') != -1:
                index = text.find(',')
                str1_split1 = text[:index]
                str1_split2 = text[index + 1:]
                text = str1_split1 + 'зпт' + str1_split2

            if text.find(' ') != -1:
                index = text.find(' ')
                str1_split1 = text[:index]
                str1_split2 = text[index + 1:]
                text = str1_split1 + 'прб' + str1_split2

    elif select == 1:
        text = text.replace(' ', '')

    if select == 1:
        Playfair_cipher(operation, text.lower().replace('й', 'и').replace('ь', 'ъ').replace('ё', 'е'))
        print()

    if select == 2:
        matrix_cipher(operation, text.lower())
        print()

