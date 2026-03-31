import random


def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def get_valid_pairs(shared_a, shared_n):
    """Заранее вычисляем все пары (K, Y) где Y != 1 и Y != a"""
    valid = []
    for k in range(2, shared_n):
        y = pow(shared_a, k, shared_n)
        if y != 1 and y != shared_a:
            valid.append((k, y))
    return valid


def check_key_collisions(Y_A, Y_B, secret_A, secret_B, shared_a):
    warnings = []
    if Y_A == secret_A:
        warnings.append(f"  ⚠ Y_A ({Y_A}) совпадает с K_A ({secret_A})!")
    if Y_B == secret_B:
        warnings.append(f"  ⚠ Y_B ({Y_B}) совпадает с K_B ({secret_B})!")
    if Y_A == secret_B:
        warnings.append(f"  ⚠ Y_A ({Y_A}) совпадает с чужим K_B ({secret_B})!")
    if Y_B == secret_A:
        warnings.append(f"  ⚠ Y_B ({Y_B}) совпадает с чужим K_A ({secret_A})!")
    if Y_A == Y_B:
        warnings.append(f"  ⚠ Y_A и Y_B совпадают ({Y_A})!")
    return warnings


def diffie_hellman():
    print("=" * 55)
    print("       ПРОТОКОЛ ОБМЕНА КЛЮЧАМИ ДИФФИ-ХЕЛЛМАНА")
    print("=" * 55)

    # --- Ввод n ---
    while True:
        try:
            shared_n = int(input("\n[Общие параметры]\nВведите простое число n: "))
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if not is_prime(shared_n):
            print("Ошибка: n должно быть простым числом!")
            continue
        if shared_n <= 2:
            print("Ошибка: n должно быть > 2!")
            continue
        break

    # --- Ввод a ---
    while True:
        try:
            shared_a = int(input(f"Введите основание a (1 < a < {shared_n}): "))
        except ValueError:
            print("Ошибка: введите целое число.")
            continue
        if not (1 < shared_a < shared_n):
            print(f"Ошибка: a должно быть в диапазоне (1, {shared_n})!")
            continue
        break

    print(f"\n  Общеизвестные параметры: n = {shared_n}, a = {shared_a}")

    # --- Предвычисляем допустимые пары (K, Y) ---
    valid_pairs = get_valid_pairs(shared_a, shared_n)

    if len(valid_pairs) < 2:
        print(f"\n  ✗ Ошибка: для n={shared_n}, a={shared_a} недостаточно")
        print(f"    допустимых значений открытых ключей.")
        print(f"    Попробуйте другое основание a или большее простое n.")
        return

    print(f"\n  Допустимые пары (K, Y): {valid_pairs}")

    # --- Цикл генерации ---
    attempt = 1
    MAX_ATTEMPTS = 100

    while attempt <= MAX_ATTEMPTS:
        if attempt > 1:
            print(f"\n  [Попытка {attempt}] Перегенерация секретных ключей...")

        # Выбираем две разные пары из допустимых
        pair_A, pair_B = random.sample(valid_pairs, 2) if len(valid_pairs) >= 2 else (valid_pairs[0], valid_pairs[0])
        secret_A, Y_A = pair_A
        secret_B, Y_B = pair_B

        print(f"\n[Шаг 1-2] Секретные ключи (не передаются!):")
        print(f"  K_A = {secret_A}")
        print(f"  K_B = {secret_B}")

        print(f"\n[Шаг 3] Открытые ключи (Y = a^K mod n):")
        print(f"  Y_A = {shared_a}^{secret_A} mod {shared_n} = {Y_A}")
        print(f"  Y_B = {shared_a}^{secret_B} mod {shared_n} = {Y_B}")

        # --- Проверка совпадений ---
        print(f"\n[Проверка совпадений ключей]:")
        warnings = check_key_collisions(Y_A, Y_B, secret_A, secret_B, shared_a)

        if warnings:
            for w in warnings:
                print(w)
            print("  → Совпадения найдены, повтор генерации...")
            attempt += 1
            continue
        else:
            print("  ✓ Совпадений не обнаружено — ключи безопасны.")

        # Шаг 4
        print(f"\n[Шаг 4] Обмен по открытому каналу:")
        print(f"  A отправляет B: Y_A = {Y_A}")
        print(f"  B отправляет A: Y_B = {Y_B}")

        # Шаг 5
        K_A = pow(Y_B, secret_A, shared_n)
        K_B = pow(Y_A, secret_B, shared_n)

        print(f"\n[Шаг 5] Вычисление общего секретного ключа K:")
        print(f"  A вычисляет: K_A = Y_B^K_A mod n = {Y_B}^{secret_A} mod {shared_n} = {K_A}")
        print(f"  B вычисляет: K_B = Y_A^K_B mod n = {Y_A}^{secret_B} mod {shared_n} = {K_B}")

        print(f"\n[Доказательство]:")
        print(f"  A: Y_B^K_A mod n = (a^K_B)^K_A mod n = a^(K_A*K_B) mod n = {K_A}")
        print(f"  B: Y_A^K_B mod n = (a^K_A)^K_B mod n = a^(K_B*K_A) mod n = {K_B}")

        # Проверка K
        print(f"\n[Проверка совпадений общего ключа K]:")
        k_warnings = []
        if K_A == 1:
            k_warnings.append(f"  ⚠ K = 1 — вырожденный ключ!")
        if K_A == Y_A:
            k_warnings.append(f"  ⚠ K ({K_A}) совпадает с Y_A ({Y_A})!")
        if K_A == Y_B:
            k_warnings.append(f"  ⚠ K ({K_A}) совпадает с Y_B ({Y_B})!")
        if K_A == secret_A:
            k_warnings.append(f"  ⚠ K ({K_A}) совпадает с K_A ({secret_A})!")
        if K_A == secret_B:
            k_warnings.append(f"  ⚠ K ({K_A}) совпадает с K_B ({secret_B})!")

        if k_warnings:
            for w in k_warnings:
                print(w)
            print("  → Общий ключ небезопасен, повтор генерации...")
            attempt += 1
            continue
        else:
            print("  ✓ Общий ключ не совпадает ни с одним из известных значений.")

        # Итоговая проверка
        print(f"\n[Проверка]: K_A = K_B = K?")
        if K_A == K_B:
            print(f"  ✓ Успех! Общий секретный ключ K = {K_A}")
            print("=" * 55)
            return
        else:
            print(f"  ✗ K_A ({K_A}) ≠ K_B ({K_B}), повтор...")
            attempt += 1

    # Если за MAX_ATTEMPTS не нашли — сообщаем
    print(f"\n  ✗ Не удалось подобрать безопасные ключи за {MAX_ATTEMPTS} попыток.")
    print(f"    Рекомендуется использовать большее простое число n.")
    print("=" * 55)


diffie_hellman()