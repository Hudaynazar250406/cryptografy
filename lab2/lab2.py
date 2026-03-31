import sys


def decryption_format(dec_text: str) -> str:
    """Восстановление точек, запятых, пробелов и заглавных букв."""
    if not dec_text:
        return dec_text

    dec_text = dec_text.replace('тчк', '.')
    dec_text = dec_text.replace('зпт', ',')
    dec_text = dec_text.replace('прб', ' ')

    # Первая буква – заглавная
    result = dec_text[0].upper() + dec_text[1:]

    result_list = list(result)
    # После точки через один символ делаем букву заглавной
    for i in range(len(result_list) - 2):
        if result_list[i] == "." and i + 2 < len(result_list):
            result_list[i + 2] = result_list[i + 2].upper()

    return "".join(result_list)


def generate_alph_matrix(string_alph: str):
    """Генерация таблицы Виженера (циклические сдвиги алфавита)."""
    n = len(string_alph)
    alphabet = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            alphabet[i][j] = string_alph[(j + i) % n]
    return alphabet


RUS_ALPH = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
ALPH_MATRIX = generate_alph_matrix(RUS_ALPH)


def Trithemius_cipher(text: str, operation: int):
    """Шифр Тритемия."""
    answer = ""

    if operation == 1:  # шифрование
        k = 0
        for i in range(len(text)):
            ch = text[i]
            if ch not in RUS_ALPH:
                raise ValueError(f"Символ '{ch}' не входит в алфавит.")
            answer += ALPH_MATRIX[i % len(RUS_ALPH)][ALPH_MATRIX[0].index(ch)]

        print("Зашифрованный текст:", end=" ")
        for ch in answer:
            print(ch, end="")
            k += 1
            if k % 5 == 0:
                print(" ", end="")
        print()

    elif operation == 2:  # расшифрование
        for i in range(len(text)):
            ch = text[i]
            if ch not in RUS_ALPH:
                raise ValueError(f"Символ '{ch}' не входит в алфавит.")
            answer += ALPH_MATRIX[0][ALPH_MATRIX[i % len(RUS_ALPH)].index(ch)]

        result = decryption_format(answer)

        print("Расшифрованный текст:", result)
    else:
        print("Неизвестная операция.")


def Belazo_cipher(text: str, operation: int):
    """Шифр Белазо (Виженер с ключевым словом)."""
    key = input("Введите ключевое слово (только русские буквы): ").lower()
    if not key:
        print("Ключ не может быть пустым.")
        return
    for ch in key:
        if ch not in RUS_ALPH:
            print(f"Недопустимый символ в ключе: '{ch}'")
            return

    answer = ""

    if operation == 1:  # шифрование
        k = 0
        for i in range(len(text)):
            t_ch = text[i]
            if t_ch not in RUS_ALPH:
                raise ValueError(f"Символ '{t_ch}' не входит в алфавит.")
            key_ch = key[i % len(key)]
            answer += ALPH_MATRIX[ALPH_MATRIX[0].index(key_ch)][ALPH_MATRIX[0].index(t_ch)]

        print("Зашифрованный текст:", end=" ")
        for ch in answer:
            print(ch, end="")
            k += 1
            if k % 5 == 0:
                print(" ", end="")
        print()

    elif operation == 2:  # расшифрование
        for i in range(len(text)):
            t_ch = text[i]
            if t_ch not in RUS_ALPH:
                raise ValueError(f"Символ '{t_ch}' не входит в алфавит.")
            key_ch = key[i % len(key)]
            answer += ALPH_MATRIX[0][ALPH_MATRIX[ALPH_MATRIX[0].index(key_ch)].index(t_ch)]

        result = decryption_format(answer)
        print("Расшифрованный текст:", result)
    else:
        print("Неизвестная операция.")


def Vigenere(text: str, operation: int):
    """Автоключ Виженера (ключ дополняется открытым текстом)."""
    key = input("Введите ключ: ").lower()
    if not key:
        print("Ключ не может быть пустым.")
        return
    for ch in key:
        if ch not in RUS_ALPH:
            print(f"Недопустимый символ в ключе: '{ch}'")
            return

    answer = ""

    if operation == 1:  # шифрование
        k = 0
        # автоключ по открытому тексту
        key_full = key + text[:-1]
        for i in range(len(text)):
            t_ch = text[i]
            if t_ch not in RUS_ALPH:
                raise ValueError(f"Символ '{t_ch}' не входит в алфавит.")
            key_ch = key_full[i]
            answer += ALPH_MATRIX[ALPH_MATRIX[0].index(key_ch)][ALPH_MATRIX[0].index(t_ch)]

        print("Зашифрованный текст:", end=" ")
        for ch in answer:
            print(ch, end="")
            k += 1
            if k % 5 == 0:
                print(" ", end="")
        print()

    elif operation == 2:  # расшифрование
        key_full = list(key)
        for i in range(len(text)):
            t_ch = text[i]
            if t_ch not in RUS_ALPH:
                raise ValueError(f"Символ '{t_ch}' не входит в алфавит.")
            key_ch = key_full[i]
            open_ch = ALPH_MATRIX[ALPH_MATRIX[ALPH_MATRIX[0].index(key_ch)].index(t_ch)][0]
            answer += open_ch
            key_full.append(open_ch)

        result = decryption_format(answer)
        print("Расшифрованный текст:", result)
    else:
        print("Неизвестная операция.")


def Vigenere_2(text: str, operation: int):
    """Вариант автоключа Виженера (по шифртексту)."""
    key = input("Введите ключ: ").lower()
    if not key:
        print("Ключ не может быть пустым.")
        return
    for ch in key:
        if ch not in RUS_ALPH:
            print(f"Недопустимый символ в ключе: '{ch}'")
            return

    answer = ""

    if operation == 1:  # шифрование (автоключ по шифртексту)
        k = 0
        key_full = list(key)
        for i in range(len(text)):
            t_ch = text[i]
            if t_ch not in RUS_ALPH:
                raise ValueError(f"Символ '{t_ch}' не входит в алфавит.")
            key_ch = key_full[i]
            c_ch = ALPH_MATRIX[ALPH_MATRIX[0].index(key_ch)][ALPH_MATRIX[0].index(t_ch)]
            answer += c_ch
            key_full.append(c_ch)

        print("Зашифрованный текст:", end=" ")
        for ch in answer:
            print(ch, end="")
            k += 1
            if k % 5 == 0:
                print(" ", end="")
        print()

    elif operation == 2:  # расшифрование
        key_full = list(key)
        for i in range(len(text)):
            c_ch = text[i]
            if c_ch not in RUS_ALPH:
                raise ValueError(f"Символ '{c_ch}' не входит в алфавит.")
            key_ch = key_full[i]
            open_ch = ALPH_MATRIX[ALPH_MATRIX[ALPH_MATRIX[0].index(key_ch)].index(c_ch)][0]
            answer += open_ch
            key_full.append(c_ch)

        result = decryption_format(answer)
        print("Расшифрованный текст:", result)
    else:
        print("Неизвестная операция.")


def preprocess_text(text: str, is_encrypt: bool) -> str:
    """Замена точек/запятых/пробелов на коды при шифровании и удаление пробелов при расшифровании."""
    if is_encrypt:
        # заменяем по всем вхождениям
        text = text.replace('.', 'тчк')
        text = text.replace(',', 'зпт')
        text = text.replace(' ', 'прб')
    else:
        text = text.replace(' ', '')
    return text


def main():
    while True:
        print(
            "Выберите шифр:\n"
            "    1. Тритемия\n"
            "    2. Белазо\n"
            "    3. Виженер (автоключ по открытому тексту)\n"
            "    4. Виженер 2 (автоключ по шифртексту)\n"
            "    5. Выход\n"
        )

        try:
            select = int(input("Ваш выбор: "))
        except ValueError:
            print("Введите номер пункта (1-5).\n")
            continue

        if select == 5:
            print("Выход из программы.")
            sys.exit()

        if select not in [1, 2, 3, 4]:
            print("Неверный выбор.\n")
            continue

        print(
            "Выберите действие:\n"
            "    1. Шифрование\n"
            "    2. Расшифрование"
        )
        try:
            operation = int(input("Ваш выбор: "))
        except ValueError:
            print("Введите 1 или 2.\n")
            continue

        if operation not in [1, 2]:
            print("Неверный выбор операции.\n")
            continue

        text = input("Введите текст: ").lower()
        print()

        text = preprocess_text(text, is_encrypt=(operation == 1))

        try:
            if select == 1:
                Trithemius_cipher(text, operation)
            elif select == 2:
                Belazo_cipher(text, operation)
            elif select == 3:
                Vigenere(text, operation)
            elif select == 4:
                Vigenere_2(text, operation)
        except ValueError as e:
            print("Ошибка:", e)

        print()


if __name__ == "__main__":
    main()
