import sys
import math

list_alph = [
    "а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м", "н",
    "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы",
    "ь", "э", "ю", "я"
]


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


def mirror_matrix_1(matrix):
    def reverse(row):
        return row[::-1]

    mirrored_matrix = [reverse(row) for row in matrix]
    return mirrored_matrix


def mirror_matrix_2(matrix):
    str_0, str_1, str_2 = matrix[0], matrix[1], matrix[2]
    matrix[0], matrix[1], matrix[2] = matrix[5], matrix[4], matrix[3]
    matrix[3], matrix[4], matrix[5] = str_2, str_1, str_0
    return matrix


def Cardano_grid(operation, text):
    result_text = ""
    if len(text) > 60:
        grid_10 = [
            [0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            [1, 0, 0, 1, 0, 1, 1, 0, 0, 1],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 0, 1, 0, 0]
        ]

        if operation == 1:  # шифрование, длина > 60

            while len(text) != 0:

                table_arr = [[0] * 10 for _ in range(10)]

                for i in range(10):
                    for j in range(10):
                        if len(text) != 0:
                            table_arr[i][j] = text[0]
                            text = text[1:]
                        else:
                            table_arr[i][j] = list_alph[(i * j) % 32]

                for i in range(10):
                    for j in range(10):
                        if grid_10[i][j] == 1:
                            result_text += str(table_arr[i][j])

                for i in range(10):
                    for j in range(10):
                        if grid_10[10 - j - 1][i] == 1:
                            result_text += str(table_arr[i][j])

                for i in range(10):
                    for j in range(10):
                        if grid_10[10 - i - 1][10 - j - 1] == 1:
                            result_text += str(table_arr[i][j])

                for i in range(10):
                    for j in range(10):
                        if grid_10[j][10 - i - 1] == 1:
                            result_text += str(table_arr[i][j])

            print("Зашифрованный текст: ", ' '.join(result_text[i: i + 5] for i in range(0, len(result_text), 5)))
            print()

        if operation == 2:  # расшифрование, длина > 60

            while len(text) != 0:

                table_arr = [[0] * 10 for _ in range(10)]

                for i in range(10):
                    for j in range(10):
                        if grid_10[i][j] == 1:
                            if len(text) != 0:
                                table_arr[i][j] = text[0]
                                text = text[1:]
                            else:
                                table_arr[i][j] = list_alph[(i * j) % 32]

                for i in range(10):
                    for j in range(10):
                        if grid_10[10 - j - 1][i] == 1:
                            if len(text) != 0:
                                table_arr[i][j] = text[0]
                                text = text[1:]
                            else:
                                table_arr[i][j] = list_alph[(i * j) % 32]

                for i in range(10):
                    for j in range(10):
                        if grid_10[10 - i - 1][10 - j - 1] == 1:
                            if len(text) != 0:
                                table_arr[i][j] = text[0]
                                text = text[1:]
                            else:
                                table_arr[i][j] = list_alph[(i * j) % 32]

                for i in range(10):
                    for j in range(10):
                        if grid_10[j][10 - i - 1] == 1:
                            if len(text) != 0:
                                table_arr[i][j] = text[0]
                                text = text[1:]
                            else:
                                table_arr[i][j] = list_alph[(i * j) % 32]

                for i in range(10):
                    for j in range(10):
                        result_text += str(table_arr[i][j])

            answer = decryption_format(result_text)
            dot_pos = answer.rfind('.')
            if dot_pos != -1:
                answer = answer[:dot_pos + 1]

            print("Расшифрованный текст: ", answer)
            print()

    else:
        grid_6 = [
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 1, 0, 0, 1]
        ]

        table_arr = [[0] * 10 for _ in range(6)]

        if operation == 1:  # шифрование, длина <= 60

            for i in range(6):
                for j in range(10):
                    if grid_6[i][j] == 1:
                        if len(text) != 0:
                            table_arr[i][j] = text[0]
                            text = text[1:]
                        else:
                            table_arr[i][j] = list_alph[(i * j * i - 1) % 32]

            grid_st_2 = mirror_matrix_1(grid_6)

            for i in range(6):
                for j in range(10):
                    if grid_st_2[i][j] == 1:
                        if len(text) != 0:
                            table_arr[i][j] = text[0]
                            text = text[1:]
                        else:
                            table_arr[i][j] = list_alph[(i * j) % 32]

            grid_st_3 = mirror_matrix_2(grid_st_2)

            for i in range(6):
                for j in range(10):
                    if grid_st_3[i][j] == 1:
                        if len(text) != 0:
                            table_arr[i][j] = text[0]
                            text = text[1:]
                        else:
                            table_arr[i][j] = list_alph[(i * j * i + 4) % 32]

            grid_st_4 = mirror_matrix_2(grid_6)

            for i in range(6):
                for j in range(10):
                    if grid_st_4[i][j] == 1:
                        if len(text) != 0:
                            table_arr[i][j] = text[0]
                            text = text[1:]
                        else:
                            table_arr[i][j] = list_alph[(i * j * i * 2) % 32]

            for i in range(6):
                for j in range(10):
                    result_text += str(table_arr[i][j])

            print("Зашифрованный текст: ", ' '.join(result_text[i: i + 5] for i in range(0, len(result_text), 5)))
            print()

        if operation == 2:  # расшифрование, длина <= 60

            for i in range(6):
                for j in range(10):
                    if len(text) != 0:
                        table_arr[i][j] = text[0]
                        text = text[1:]
                    else:
                        table_arr[i][j] = list_alph[(i * j * 7) % 32]

            for i in range(6):
                for j in range(10):
                    if grid_6[i][j] == 1:
                        result_text += table_arr[i][j]

            grid_st_2 = mirror_matrix_1(grid_6)

            for i in range(6):
                for j in range(10):
                    if grid_st_2[i][j] == 1:
                        result_text += table_arr[i][j]

            grid_st_3 = mirror_matrix_2(grid_st_2)

            for i in range(6):
                for j in range(10):
                    if grid_st_3[i][j] == 1:
                        result_text += table_arr[i][j]

            grid_st_4 = mirror_matrix_2(grid_6)

            for i in range(6):
                for j in range(10):
                    if grid_st_4[i][j] == 1:
                        result_text += table_arr[i][j]

            answer = decryption_format(result_text)
            dot_pos = answer.rfind('.')
            if dot_pos != -1:
                answer = answer[:dot_pos + 1]

            print("Расшифрованный текст: ", answer)
            print()


def vertical_permutation(operation, text):

    key = input("Введите ключ: ")

    if len(key) > len(text):
        print("Неверный ключ!")
        exit()

    result_text = ""

    letter_order = {chr(i): i - ord('а') + 1 for i in range(ord('а'), ord('я') + 1)}

    result = [letter_order[char] for char in key]

    key_list = [sorted(result).index(num) + 1 for num in result]

    for i in range(len(key_list)):
        key_list[i] -= 1
        for j in range(0, i):
            if key_list[j] == key_list[i]:
                key_list[i] += 1

    cols = len(key_list)
    if len(text) % cols == 0:
        rows = (len(text) // cols)
    else:
        rows = (len(text) // cols) + 1

    table_arr = [[0] * cols for _ in range(rows)]

    k = 0
    for i in range(rows):
        for j in range(cols):
            if k < len(text):
                table_arr[i][j] = str(text[k])
                k += 1
            else:
                table_arr[i][j] = ""

    if operation == 1:

        for i in range(cols):
            for j in range(rows):
                result_text += table_arr[j][key_list.index(i)]

        print("Зашифрованный текст: ", ' '.join(result_text[i: i + 5] for i in range(0, len(result_text), 5)))
        print()

    if operation == 2:

        k = 0
        for i in range(cols):
            index = key_list.index(i)
            for j in range(rows):
                if table_arr[j][index] != "":
                    table_arr[j][index] = ""
                    table_arr[j][index] += text[k]
                    k += 1

        for i in range(rows):
            for j in range(cols):
                result_text += table_arr[i][j]

        answer = decryption_format(result_text)

        print("Расшифрованный текст: ", end=' ')
        for i in answer:
            print(i, end='')
        print()


while True:

    print("""Выберите шифр: 
             1.  Решётка Кардано
             2.  Вертикальная перестановка
             3.  Выход
         """)
    select: int = int(input("Ваш выбор: "))
    if select == 3:
        sys.exit()

    if select not in [1, 2, 3]:
        print("Неверный выбор!")
        continue

    print("""Выберите действие: 
                1. Шифрование 
                2. Расшифрование""")
    operation: int = int(input("Ваш выбор: "))
    if operation not in [1, 2]:
        print("Неверный выбор!")
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

    else:
        text = text.replace(' ', '')

    if select == 1:
        Cardano_grid(operation, text.lower())
        print()

    if select == 2:
        vertical_permutation(operation, text.lower())
        print()
