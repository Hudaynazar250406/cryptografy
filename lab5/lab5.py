import sys
import math

list_alph = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
             "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
             "ъ", "ы", "ь", "э", "ю", "я"]

M = len(list_alph)  # 32


# ══════════════════════════════════════════════════════════════
#  Вспомогательные функции
# ══════════════════════════════════════════════════════════════

def digitization_for_Shannon(open_text):
    return [list_alph.index(ch) + 1 for ch in open_text]


def undigitization_for_Shannon(ciphertext):
    return "".join(list_alph[n - 1] for n in ciphertext)


def generate_gamma_for_Shannon(a, c, t0, length):
    """T(i+1) = (a·T(i) + c) mod M"""
    t, gamma = t0, []
    for _ in range(length):
        t = (a * t + c) % M
        gamma.append(t)
    return gamma


def decryption_format(dec_text):
    dec_text    = dec_text.replace('тчк', '.').replace('зпт', ',').replace('прб', ' ')
    result_list = list(dec_text[0].upper() + dec_text[1:])
    for i in range(len(result_list) - 2):
        if result_list[i] == "." and i + 2 < len(result_list):
            result_list[i + 2] = result_list[i + 2].upper()
    return "".join(result_list)


# ══════════════════════════════════════════════════════════════
#  Валидация ключевых параметров
# ══════════════════════════════════════════════════════════════

def validate_key_params():
    """
    Условия максимального периода ЛКГ (теорема Халла–Добелла) для m = 32 = 2^5:
      • a  ≥ 5, нечётное, a ≡ 1 (mod 4)   →  допустимые: 5, 9, 13, 17, 21, 25, 29 ...
      • c  — нечётное, НОД(c, 32) = 1,  0 < c < 32
      • T0 — начальное значение,  0 ≤ T0 ≤ 31
    """

    # ── Параметр a ──────────────────────────────────────────
    while True:
        try:
            a = int(input(f"\n  Введите a  (нечётное, a ≡ 1 mod 4, a ≥ 5): "))
        except ValueError:
            print("  ✗ Введите целое число.")
            continue

        errors = []
        if a < 5:
            errors.append("a должно быть не менее 5  (a = 1 недопустимо)")
        if a % 2 != 1:
            errors.append("a должно быть нечётным числом")
        elif (a - 1) % 4 != 0:
            errors.append("(a − 1) должно делиться на 4  →  a ≡ 1 (mod 4)")

        if errors:
            print("  ✗ Ошибка параметра a:")
            for e in errors:
                print(f"      • {e}")
            print("  Подсказка: 5, 9, 13, 17, 21, 25, 29, 33 ...")
            continue

        break

    # ── Параметр c ──────────────────────────────────────────
    while True:
        try:
            c = int(input(f"  Введите c  (нечётное, взаимно простое с {M},  0 < c < {M}): "))
        except ValueError:
            print("  ✗ Введите целое число.")
            continue

        errors = []
        if not (0 < c < M):
            errors.append(f"c должно быть в диапазоне (0, {M})")
        if math.gcd(c, M) != 1:
            errors.append(f"НОД(c, {M}) ≠ 1  →  c должно быть нечётным числом")

        if errors:
            print("  ✗ Ошибка параметра c:")
            for e in errors:
                print(f"      • {e}")
            print("  Подсказка: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31")
            continue

        break

    # ── Параметр T0 ─────────────────────────────────────────
    while True:
        try:
            t0 = int(input(f"  Введите T0 (начальное значение, 0 ≤ T0 ≤ {M - 1}): "))
        except ValueError:
            print("  ✗ Введите целое число.")
            continue

        if not (0 <= t0 <= M - 1):
            print(f"  ✗ T0 должно быть в диапазоне [0, {M - 1}].")
            continue

        break

    print(f"\n  ✓ Ключ принят:  a = {a},  c = {c},  T0 = {t0}\n")
    return a, c, t0


# ══════════════════════════════════════════════════════════════
#  Шифр-блокнот Шеннона
# ══════════════════════════════════════════════════════════════

def Shannon_notebook(operation, text):
    a, c, t0 = validate_key_params()

    digital_text = digitization_for_Shannon(text)
    gen_gamma    = generate_gamma_for_Shannon(a, c, t0, len(digital_text))

    if operation == 1:
        # E_i = ((P_i − 1 + G_i) mod M) + 1  →  результат всегда в [1, M]
        encrypted_text = [((p - 1 + g) % M) + 1 for p, g in zip(digital_text, gen_gamma)]

        ciphertext     = undigitization_for_Shannon(encrypted_text)
        letters_groups = [ciphertext[i:i + 5]      for i in range(0, len(ciphertext),      5)]
        number_groups  = [encrypted_text[i:i + 5]  for i in range(0, len(encrypted_text),  5)]

        print("\nЗашифрованный текст:")
        print("  Буквы: ", ' '.join(''.join(grp) for grp in letters_groups))
        print("  Цифры: ", '  '.join(' '.join(str(n) for n in grp) for grp in number_groups))
        print()

    elif operation == 2:
        # P_i = ((E_i − 1 − G_i) mod M) + 1
        dec_text  = [((e - 1 - g) % M) + 1 for e, g in zip(digital_text, gen_gamma)]
        open_text = undigitization_for_Shannon(dec_text)
        answer    = decryption_format(open_text)

        print("Расшифрованный текст:", answer)
        print()


# ══════════════════════════════════════════════════════════════
#  Главный цикл
# ══════════════════════════════════════════════════════════════

while True:
    print("─" * 40)
    print("Выберите шифр:")
    print("  1. Шифр-блокнот Шеннона")
    print("  2. Выход")
    print("─" * 40)

    try:
        select = int(input("Ваш выбор: "))
    except ValueError:
        print("✗ Ошибка: введите число.\n")
        continue

    if select == 2:
        print("До свидания!")
        sys.exit()

    if select != 1:
        print("✗ Неверный выбор!\n")
        continue

    print("\nВыберите действие:")
    print("  1. Шифрование")
    print("  2. Дешифрование")

    try:
        operation = int(input("Ваш выбор: "))
    except ValueError:
        print("✗ Ошибка: введите число.\n")
        continue

    if operation not in (1, 2):
        print("✗ Неверный выбор!\n")
        continue

    text = input("\nВведите текст: ").lower()
    print()

    if operation == 1:
        text = text.replace('.', 'тчк').replace(',', 'зпт').replace(' ', 'прб')
    else:
        text = text.replace(' ', '')

    Shannon_notebook(operation, text)
