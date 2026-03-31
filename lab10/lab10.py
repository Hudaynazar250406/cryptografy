import random
import sys


def hash_quad(text: str, p: int, verbose: bool = False) -> int:
    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    h = 0
    if verbose:
        print(f"\n  Формула: h_i = (h_{{i-1}} + индекс(буквы) + 1)² mod {p}")
        print(f"  {'Буква':<6} {'Индекс':<8} {'Вычисление':<38} {'h'}")
        print("  " + "-"*65)
    for ch in text:
        idx = alphabet.index(ch) + 1
        h_prev = h
        h = ((h_prev + idx) ** 2) % p
        if verbose:
            calc = f"({h_prev} + {idx})² % {p} = {(h_prev+idx)**2} % {p}"
            print(f"  '{ch}'    {idx:<8} {calc:<38} {h}")
    result = h if h != 0 else 1
    if verbose and h == 0:
        print("  h = 0 → заменяем на 1")
    return result


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def mod_inv(a: int, p: int) -> int:
    a = a % p
    if a == 0:
        raise ZeroDivisionError("Обратный элемент не существует")
    return pow(a, -1, p)


def compute_a(p: int, q: int) -> int:
    print(f"\n{'='*60}")
    print(f"  АВТОВЫЧИСЛЕНИЕ ПАРАМЕТРА a")
    print(f"{'='*60}")
    print(f"  Формула: a = d^((p-1)/q) mod p")
    print(f"  Условие: a != 1  и  a^q mod p = 1")
    print(f"  (p-1)/q = ({p}-1)/{q} = {(p-1)//q}\n")
    exp = (p - 1) // q
    print(f"  {'d':<6} {'Вычисление':<30} {'a':<8} {'a^q mod p':<12} {'Статус'}")
    print(f"  {'-'*65}")
    for d in range(2, p):
        a = pow(d, exp, p)
        check = pow(a, q, p)
        ok = (a != 1) and (check == 1)
        print(f"  {d:<6} {d}^{exp} mod {p:<6} {a:<8} {check:<12} {'✓ принят' if ok else '✗ пропуск'}")
        if ok:
            print(f"\n  >>> a = {a}  (при d = {d})")
            print(f"  Проверка: {a}^{q} mod {p} = {check} = 1  ✓")
            return a
    raise ValueError("Не удалось найти подходящее a!")


def point_add(P, Q, a: int, p: int):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = int(P[0]) % p, int(P[1]) % p
    x2, y2 = int(Q[0]) % p, int(Q[1]) % p
    if x1 == x2:
        if y1 != y2 or y1 == 0:
            return None
        try:
            lam = (3 * x1 * x1 + a) % p * mod_inv(2 * y1, p) % p
        except ZeroDivisionError:
            return None
    else:
        try:
            lam = (y2 - y1) % p * mod_inv(x2 - x1, p) % p
        except ZeroDivisionError:
            return None
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return [int(x3), int(y3)]


def scalar_mult(k: int, P, a: int, p: int):
    if k == 0:
        return None
    if k < 0:
        k = -k
        P = [int(P[0]) % p, (-int(P[1])) % p]
    result = None
    addend = [int(P[0]) % p, int(P[1]) % p]
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result


def compute_order(G, a: int, p: int) -> int:
    print(f"\n{'='*60}")
    print(f"  ВЫЧИСЛЕНИЕ ПОРЯДКА q ТОЧКИ G={G}")
    print(f"{'='*60}")
    print(f"  Ищем наименьшее q такое, что q·G = O\n")
    print(f"  {'k':<5} {'k·G'}")
    print(f"  {'-'*30}")
    current = [int(G[0]) % p, int(G[1]) % p]
    for k in range(1, 10000):
        print(f"  {k:<5} {current}")
        nxt = point_add(current, G, a, p)
        if nxt is None:
            q = k + 1
            print(f"  {k+1:<5} O  ← точка на бесконечности!")
            print(f"\n  >>> q = {q}")
            return q
        current = nxt
    raise ValueError("Порядок точки слишком большой (> 10000)")


def get_curve_points(a: int, b: int, p: int):
    pts = []
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                pts.append([x, y])
    return pts


# ─────────────────────────────────────────
#  ГОСТ Р 34.10-94
# ─────────────────────────────────────────
def GOSTR_34_10_94(operation: int, text: str):
    p = int(input(" - Введите P (простое, P > 32): "))
    if not is_prime(p):
        print("P должно быть простым!")
        return
    if p <= 32:
        print(f"P должно быть > 32! Вы ввели {p}")
        return

    q = int(input(f" - Введите Q (простой делитель {p-1}): "))
    if not is_prime(q) or (p - 1) % q != 0:
        print(f"Q должно быть простым делителем {p-1}!")
        return

    a = compute_a(p, q)

    print(f"\n{'='*60}")
    print(f"  ШАГ 1: ВЫЧИСЛЕНИЕ ХЕША  (mod q={q})")
    print(f"{'='*60}")
    m = hash_quad(text, q, verbose=True)
    print(f"\n  >>> m = {m}")

    if operation == 1:
        x = int(input(f"\n - Введите X (закрытый ключ, 0 < X < {q}): "))
        if not (0 < x < q):
            print("X должен быть в диапазоне (0, q)!")
            return

        print(f"\n{'='*60}")
        print(f"  ШАГ 2: ОТКРЫТЫЙ КЛЮЧ")
        print(f"{'='*60}")
        y = pow(a, x, p)
        print(f"  Y = a^x mod p = {a}^{x} mod {p} = {y}")

        print(f"\n{'='*60}")
        print(f"  ШАГ 3: ПОДПИСАНИЕ")
        print(f"{'='*60}")
        print(f"  r = (a^k mod p) mod q")
        print(f"  s = (x·r + k·m) mod q\n")
        print(f"  {'k':<5} {'a^k mod p':<12} {'r':<6} {'s':<6} {'Статус'}")
        print(f"  {'-'*50}")

        candidates = list(range(1, q))
        random.shuffle(candidates)
        r, s, chosen_k = 0, 0, None
        for k in candidates:
            r_try = pow(a, k, p) % q
            s_try = (x * r_try + k * m) % q
            ok = r_try != 0 and s_try != 0
            print(f"  {k:<5} {pow(a,k,p):<12} {r_try:<6} {s_try:<6} {'✓ принят' if ok else '✗ пропуск'}")
            if ok:
                r, s, chosen_k = r_try, s_try, k
                break

        if chosen_k is None:
            print("\n  Ошибка: не найден подходящий k! Проверьте параметры.")
            return

        print(f"\n  Выбран k = {chosen_k}")
        print(f"\n  r = ({a}^{chosen_k} mod {p}) mod {q}")
        print(f"  r = {pow(a, chosen_k, p)} mod {q} = {r}")
        print(f"\n  s = ({x}·{r} + {chosen_k}·{m}) mod {q}")
        print(f"  s = ({x*r} + {chosen_k*m}) mod {q}")
        print(f"  s = {x*r + chosen_k*m} mod {q} = {s}")

        print(f"\n{'='*60}")
        print(f"  РЕЗУЛЬТАТ")
        print(f"{'='*60}")
        print(f"  Y (открытый ключ) = {y}")
        print(f"  Подпись: r = {r}, s = {s}")

    elif operation == 2:
        sig = list(map(int, input(" - Введите подпись (r s): ").split()))
        r, s = sig[0], sig[1]
        y = int(input(" - Введите Y (открытый ключ): "))

        print(f"\n{'='*60}")
        print(f"  ШАГ 2: ПРОВЕРКА ДИАПАЗОНА")
        print(f"{'='*60}")
        print(f"  0 < r={r} < q={q}  →  {'ОК' if 0 < r < q else 'ОШИБКА'}")
        print(f"  0 < s={s} < q={q}  →  {'ОК' if 0 < s < q else 'ОШИБКА'}")
        if not (0 < r < q and 0 < s < q):
            print("  Подпись недействительна!")
            return

        print(f"\n{'='*60}")
        print(f"  ШАГ 3: ВЫЧИСЛЕНИЕ v, z1, z2, u")
        print(f"{'='*60}")
        v = pow(m, q - 2, q)
        print(f"  v = m^(q-2) mod q = {m}^{q-2} mod {q} = {v}")
        z1 = (s * v) % q
        z2 = ((q - r) * v) % q
        print(f"  z1 = s·v mod q = {s}·{v} mod {q} = {z1}")
        print(f"  z2 = (q-r)·v mod q = ({q}-{r})·{v} mod {q} = {z2}")
        az1 = pow(a, z1, p)
        yz2 = pow(y, z2, p)
        u = az1 * yz2 % p % q
        print(f"\n  u = (a^z1 · y^z2 mod p) mod q")
        print(f"  u = ({a}^{z1} · {y}^{z2} mod {p}) mod {q}")
        print(f"  u = ({az1} · {yz2} mod {p}) mod {q}")
        print(f"  u = {az1 * yz2 % p} mod {q} = {u}")

        print(f"\n{'='*60}")
        print(f"  РЕЗУЛЬТАТ: u={u} == r={r}  →  ", end="")
        print("ПОДПИСЬ ВЕРНА ✓" if u == r else "ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА ✗")


# ─────────────────────────────────────────
#  ГОСТ Р 34.10-2012
# ─────────────────────────────────────────
def GOSTR_34_10_2012(operation: int, text: str):
    a = int(input(" - Введите a (коэффициент кривой): "))
    b = int(input(" - Введите b (коэффициент кривой): "))
    p = int(input(" - Введите p (простое): "))
    if not is_prime(p):
        print("p должно быть простым!")
        return

    g_raw = list(map(int, input(" - Введите G (базовая точка, x y через пробел): ").split()))
    G = [g_raw[0], g_raw[1]]

    print(f"\n{'='*60}")
    print(f"  КРИВАЯ: y² = x³ + {a}x + {b} (mod {p})")
    print(f"{'='*60}")
    pts = get_curve_points(a, b, p)
    print(f"  Все точки кривой (+ O):")
    for pt in pts:
        print(f"    {pt}")
    print(f"    O (бесконечность)")
    print(f"  Всего точек: {len(pts) + 1}")

    q = compute_order(G, a, p)

    print(f"\n{'='*60}")
    print(f"  ШАГ 1: ВЫЧИСЛЕНИЕ ХЕША  (mod p={p})")
    print(f"{'='*60}")
    m = hash_quad(text, p, verbose=True)
    print(f"\n  >>> m = {m}")

    if operation == 1:
        x_a = int(input(f"\n - Введите x_A (закрытый ключ, 0 < x_A < {q}): "))
        if not (0 < x_a < q):
            print(f"x_A должен быть в (0, {q})!")
            return

        print(f"\n{'='*60}")
        print(f"  ШАГ 2: ОТКРЫТЫЙ КЛЮЧ")
        print(f"{'='*60}")
        Y_a = scalar_mult(x_a, G, a, p)
        print(f"  Y_A = x_A · G = {x_a} · {G} = {Y_a}")

        k_input = input(f"\n - Введите k (1 ≤ k < {q}, или Enter для случайного): ").strip()
        fixed_k = int(k_input) if k_input else None

        print(f"\n{'='*60}")
        print(f"  ШАГ 3: ПОДПИСАНИЕ")
        print(f"{'='*60}")
        print(f"  C = k·G,  r = C.x mod q,  s = (k·m + r·x_A) mod q\n")
        print(f"  {'k':<5} {'C = k·G':<18} {'r':<6} {'s':<6} {'Статус'}")
        print(f"  {'-'*55}")

        if fixed_k is not None:
            candidates = [fixed_k]
        else:
            candidates = list(range(1, q))
            random.shuffle(candidates)

        r, s, chosen_k, C_chosen = 0, 0, None, None
        for k in candidates:
            C = scalar_mult(k, G, a, p)
            if C is None:
                print(f"  {k:<5} {'O':<18} {'-':<6} {'-':<6} ✗ C=O")
                continue
            r_try = C[0] % q
            s_try = (k * m + r_try * x_a) % q
            ok = r_try != 0 and s_try != 0
            print(f"  {k:<5} {str(C):<18} {r_try:<6} {s_try:<6} {'✓ принят' if ok else '✗ пропуск'}")
            if ok:
                r, s, chosen_k, C_chosen = r_try, s_try, k, C
                break

        if chosen_k is None:
            print("\n  Ошибка: не найден подходящий k! Проверьте параметры.")
            return

        print(f"\n  Выбран k = {chosen_k}")
        print(f"  C = {chosen_k}·{G} = {C_chosen}")
        print(f"  r = C.x mod q = {C_chosen[0]} mod {q} = {r}")
        print(f"\n  s = (k·m + r·x_A) mod q")
        print(f"  s = ({chosen_k}·{m} + {r}·{x_a}) mod {q}")
        print(f"  s = ({chosen_k*m} + {r*x_a}) mod {q}")
        print(f"  s = {chosen_k*m + r*x_a} mod {q} = {s}")

        print(f"\n{'='*60}")
        print(f"  РЕЗУЛЬТАТ")
        print(f"{'='*60}")
        print(f"  Открытый ключ Y_A = {Y_a}")
        print(f"  Подпись: r = {r}, s = {s}")

    elif operation == 2:
        sig = list(map(int, input(" - Введите подпись (r s): ").split()))
        r, s = sig[0], sig[1]
        y_raw = list(map(int, input(" - Введите Y (x y через пробел): ").split()))
        Y_a = [y_raw[0], y_raw[1]]

        print(f"\n{'='*60}")
        print(f"  ШАГ 2: ПРОВЕРКА ДИАПАЗОНА")
        print(f"{'='*60}")
        print(f"  0 < r={r} < q={q}  →  {'ОК' if 0 < r < q else 'ОШИБКА'}")
        print(f"  0 < s={s} < q={q}  →  {'ОК' if 0 < s < q else 'ОШИБКА'}")
        if not (0 < r < q and 0 < s < q):
            print("  Подпись недействительна!")
            return

        print(f"\n{'='*60}")
        print(f"  ШАГ 3: ВЫЧИСЛЕНИЕ u1, u2, R")
        print(f"{'='*60}")
        h_inv = pow(m, q - 2, q)
        print(f"  h⁻¹ = m^(q-2) mod q = {m}^{q-2} mod {q} = {h_inv}")
        u1 = (s * h_inv) % q
        u2 = (-r * h_inv) % q
        print(f"\n  u1 = s · h⁻¹ mod q = {s}·{h_inv} mod {q} = {u1}")
        print(f"  u2 = -r · h⁻¹ mod q = (-{r})·{h_inv} mod {q} = {u2}")

        A1 = scalar_mult(u1, G, a, p)
        A2 = scalar_mult(u2, Y_a, a, p)
        R  = point_add(A1, A2, a, p)

        print(f"\n  A1 = u1·G   = {u1}·{G}   = {A1}")
        print(f"  A2 = u2·Y_A = {u2}·{Y_a} = {A2}")
        print(f"  R  = A1 + A2 = {R}")

        if R is None:
            print("\n  R = O → ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА ✗")
            return

        print(f"\n  R.x mod q = {R[0]} mod {q} = {R[0] % q}")
        print(f"\n{'='*60}")
        print(f"  РЕЗУЛЬТАТ: {R[0] % q} == r={r}  →  ", end="")
        print("ПОДПИСЬ ВЕРНА ✓" if R[0] % q == r else "ПОДПИСЬ НЕДЕЙСТВИТЕЛЬНА ✗")


# ─────────────────────────────────────────
#  Обработка текста
# ─────────────────────────────────────────
def preprocess(text: str) -> str:
    text = text.replace('.', 'тчк')
    text = text.replace(',', 'зпт')
    text = text.replace(' ', 'прб')
    return text.lower()


# ─────────────────────────────────────────
#  Главный цикл
# ─────────────────────────────────────────
while True:
    print("""
╔══════════════════════════════════╗
║    Выберите алгоритм ЭЦП:        ║
║  1. ГОСТ Р 34.10-94              ║
║  2. ГОСТ Р 34.10-2012            ║
║  3. Выход                        ║
╚══════════════════════════════════╝""")
    try:
        select = int(input(">> "))
    except ValueError:
        print("Введите число!")
        continue

    if select == 3:
        sys.exit()

    if select not in [1, 2]:
        print("Неверный выбор!")
        continue

    print("""
╔══════════════════════════════════╗
║    Выберите действие:            ║
║  1. Подписание                   ║
║  2. Проверка подписи             ║
╚══════════════════════════════════╝""")
    try:
        operation = int(input(">> "))
    except ValueError:
        print("Введите число!")
        continue

    if operation not in [1, 2]:
        print("Неверный выбор!")
        continue

    text = input("Введите текст: ")
    text = preprocess(text)
    print(f" Обработанный текст: {text}\n")

    if select == 1:
        GOSTR_34_10_94(operation, text)
    elif select == 2:
        GOSTR_34_10_2012(operation, text)

    print()
9