# -*- coding: utf-8 -*-

# ========================== НАСТРОЙКИ ==========================
ALPHABET = "абвгдежзиклмнопрстуфхцчшщъыэюя"  # ровно 30 символов
ROWS = 5
COLS = 6
PAD_CHAR = 'ъ'
# ===============================================================


def normalize_char(c):
    if c == 'ё': return 'е'
    if c == 'й': return 'и'
    if c == 'ь': return 'ъ'
    return c


def normalize_text(text):
    return ''.join(normalize_char(ch) for ch in text.lower())


def prepare_plaintext(original):
    result = []
    for ch in original.lower():
        if ch == ',':
            result.append('зпт')
        elif ch == '.':
            result.append('тчк')
        elif ch == ' ':
            continue
        else:
            result.append(normalize_char(ch))
    return ''.join(result)


def postprocess_decrypted(text):
    """
    Обработка расшифрованного текста:
    1. Удаление ВСЕХ вставных PAD_CHAR (ъ между одинаковыми буквами и в конце)
    2. Замена служебных последовательностей: зпт -> ,  тчк -> .
    3. Восстановление регистра
    """
    # Убираем ъ, вставленные между одинаковыми буквами (AъA -> AA)
    # и финальные ъ (заполнитель чётности)
    result = []
    i = 0
    while i < len(text):
        if text[i] == PAD_CHAR:
            # Проверяем: ъ между двумя одинаковыми буквами?
            prev_ch = result[-1] if result else None
            next_ch = text[i + 1] if i + 1 < len(text) else None
            if prev_ch is not None and next_ch is not None and prev_ch == next_ch:
                # Разделитель между одинаковыми — пропускаем
                i += 1
                continue
            else:
                # Финальный заполнитель или одиночный — пропускаем
                i += 1
                continue
        else:
            result.append(text[i])
            i += 1

    text = ''.join(result)

    # Замена служебных последовательностей
    text = text.replace('зпт', ',').replace('тчк', '.')

    # Восстановление регистра
    if not text:
        return text
    result = list(text)
    result[0] = result[0].upper()
    for i in range(len(result) - 2):
        if result[i] == '.':
            result[i + 2] = result[i + 2].upper()
    return ''.join(result)


def build_table(keyword):
    key_raw = []
    for ch in keyword.lower():
        ch_norm = normalize_char(ch)
        if ch_norm in ALPHABET:
            key_raw.append(ch_norm)
        else:
            raise ValueError(f"Недопустимый символ в ключе: {ch}")

    if len(set(key_raw)) != len(key_raw):
        raise ValueError("В ключе есть повторяющиеся буквы. Ключ должен содержать только уникальные символы.")

    seen = set(key_raw)
    key = list(key_raw)

    for ch in ALPHABET:
        if ch not in seen:
            key.append(ch)

    table = []
    idx = 0
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(key[idx])
            idx += 1
        table.append(row)
    return table


def find_pos(table, ch):
    for r in range(ROWS):
        for c in range(COLS):
            if table[r][c] == ch:
                return r, c
    raise ValueError(f"Символ '{ch}' не найден в таблице")


def prepare_bigrams(text):
    res = []
    i = 0
    while i < len(text):
        a = text[i]
        if i == len(text) - 1:
            res.append(a)
            res.append(PAD_CHAR)
            i += 1
        else:
            b = text[i + 1]
            if a == b:
                res.append(a)
                res.append(PAD_CHAR)
                i += 1
            else:
                res.append(a)
                res.append(b)
                i += 2
    return ''.join(res)


def encrypt_playfair(plain, table):
    if len(plain) % 2 != 0:
        raise ValueError("Длина должна быть чётной")
    cipher = []
    for i in range(0, len(plain), 2):
        a, b = plain[i], plain[i + 1]
        r1, c1 = find_pos(table, a)
        r2, c2 = find_pos(table, b)
        if r1 == r2:
            cipher.append(table[r1][(c1 + 1) % COLS])
            cipher.append(table[r2][(c2 + 1) % COLS])
        elif c1 == c2:
            cipher.append(table[(r1 + 1) % ROWS][c1])
            cipher.append(table[(r2 + 1) % ROWS][c2])
        else:
            cipher.append(table[r1][c2])
            cipher.append(table[r2][c1])
    return ''.join(cipher)


def decrypt_playfair(cipher, table):
    if len(cipher) % 2 != 0:
        raise ValueError("Длина шифртекста должна быть чётной")
    plain = []
    for i in range(0, len(cipher), 2):
        a, b = cipher[i], cipher[i + 1]
        r1, c1 = find_pos(table, a)
        r2, c2 = find_pos(table, b)
        if r1 == r2:
            plain.append(table[r1][(c1 - 1) % COLS])
            plain.append(table[r2][(c2 - 1) % COLS])
        elif c1 == c2:
            plain.append(table[(r1 - 1) % ROWS][c1])
            plain.append(table[(r2 - 1) % ROWS][c2])
        else:
            plain.append(table[r1][c2])
            plain.append(table[r2][c1])
    return ''.join(plain)


def print_encryption_details(plain, cipher, table):
    if len(plain) % 2 != 0 or len(cipher) % 2 != 0:
        print("Ошибка: нечётная длина")
        return
    print("\n" + "=" * 70)
    print("Детали шифрования по биграммам:")
    print("№  | Пара | Координаты           | Правило              | Результат")
    print("-" * 70)
    for i in range(0, len(plain), 2):
        a, b = plain[i], plain[i + 1]
        r1, c1 = find_pos(table, a)
        r2, c2 = find_pos(table, b)
        res_a, res_b = cipher[i], cipher[i + 1]
        if r1 == r2:
            rule = "одна строка → вправо"
        elif c1 == c2:
            rule = "один столбец → вниз"
        else:
            rule = "прямоугольник"
        num = i // 2 + 1
        coord = f"({r1},{c1}) и ({r2},{c2})"
        print(f"{num:2} |  {a}{b}  | {coord:20} | {rule:20} | {res_a}{res_b}")
    print("=" * 70)


def main():
    print("========== Шифр Плейфера (русский язык, таблица 5x6) ==========")
    print("Замены: ё -> е, й -> и, ь -> ъ")
    print("Знаки препинания: , -> зпт, . -> тчк; пробелы удаляются.")
    print(f"Символ-заполнитель: '{PAD_CHAR}'")
    print("В ключе не должно быть повторяющихся букв.")
    print("-" * 60)

    while True:
        print("\nМеню:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            while True:
                key = input("Введите ключевое слово (только русские буквы, без повторов): ").strip()
                if not key:
                    print("Ключ не может быть пустым.")
                    continue
                try:
                    table = build_table(key)
                    break
                except ValueError as e:
                    print("Ошибка в ключе:", e)

            print("\nТаблица шифрования (5x6):")
            for row in table:
                print(' '.join(row))

            plain = input("Введите открытый текст: ").strip()
            prepared = prepare_plaintext(plain)
            print("\nПосле замены знаков и нормализации:", prepared)
            bigram_ready = prepare_bigrams(prepared)
            print(f"После вставки заполнителя (длина {len(bigram_ready)}): {bigram_ready}")
            cipher = encrypt_playfair(bigram_ready, table)
            pairs = [cipher[i:i + 2] for i in range(0, len(cipher), 2)]
            print("\nЗашифрованный текст (биграммы через пробел):")
            print(' '.join(pairs))
            print("Полный шифртекст (слитно):", cipher)
            print_encryption_details(bigram_ready, cipher, table)

        elif choice == '2':
            while True:
                key = input("Введите ключевое слово (только русские буквы, без повторов): ").strip()
                if not key:
                    print("Ключ не может быть пустым.")
                    continue
                try:
                    table = build_table(key)
                    break
                except ValueError as e:
                    print("Ошибка в ключе:", e)

            print("\nТаблица шифрования (5x6):")
            for row in table:
                print(' '.join(row))

            cipher = input("Введите шифртекст (только буквы, можно с пробелами): ").strip()
            cipher = ''.join(cipher.split())
            if len(cipher) % 2 != 0:
                print("Ошибка: длина шифртекста нечётная.")
                continue

            decrypted_bigram = decrypt_playfair(cipher, table)
            print("\nПосле расшифрования (с заполнителем):", decrypted_bigram)
            final_text = postprocess_decrypted(decrypted_bigram)
            print("Расшифрованный текст:", final_text)

        elif choice == '3':
            break
        else:
            print("Неверный выбор. Повторите.")


if __name__ == "__main__":
    main()
