from typing import List
import sys
import sympy
from math import gcd

alphabet: str = "абвгдежзийклмнопрстуфхцчшщъыьэюя"  # 32 буквы (с й)
MIN_N = 32


def hash_quad(text: str, p: int) -> int:
    tec_h = 0
    for ch in text:
        tec_h = ((tec_h + alphabet.index(ch) + 1) ** 2) % p
    return int(tec_h)


def euclid(a: int, b: int) -> List[int]:
    res: List[int] = []
    while a != 0 and b != 0:
        if a > b: res.append(a // b); a %= b
        else: res.append(b // a); b %= a
    return res


def eq(a: int, b: int, m: int) -> int:
    q: List[int] = euclid(a, m)
    if m < a: q.insert(0, 0)
    p: List = [1, q[0]]
    for i in range(1, len(q)):
        p.append(p[i] * q[i] + p[i - 1])
    return ((-1) ** (len(q) - 1) * p[-2] * b) % m


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d ** 2 <= n and n % d != 0: d += 2
    return d ** 2 > n


def comparisons(a, b, m):
    divider, divisible = m, a
    rem = divider % divisible
    n, arr_q, arr_rem = 0, [], []
    while rem != 0:
        integer = divider // divisible
        rem = divider % divisible
        arr_rem.append(rem); arr_q.append(integer)
        divider, divisible = divisible, rem
        n += 1
    if a % arr_rem[-2] != 0 or b % arr_rem[-2] != 0 or m % arr_rem[-2] != 0:
        print("  Сравнение не имеет решений"); return 0
    a /= arr_rem[-2]; b /= arr_rem[-2]; m /= arr_rem[-2]
    p = [1, arr_q[0]]
    for i in range(2, n + 1):
        p.append(arr_q[i - 1] * p[i - 1] + p[i - 2])
    return int(((-1) ** (n - 1) * p[-2] * b) % m)


# ─────────────────────────────────────────────
#  RSA ЦИФРОВАЯ ПОДПИСЬ
# ─────────────────────────────────────────────

def RSA(operation, text):
    print("\n── RSA ЦИФРОВАЯ ПОДПИСЬ ──")

    if operation == 1:
        while True:
            p = int(input("  Введите P (простое): "))
            q = int(input("  Введите Q (простое): "))
            if not is_prime(p) or not is_prime(q):
                print("  ❌ P и Q должны быть простыми!"); continue
            n = p * q
            if n < MIN_N:
                print(f"  ❌ N = {p}×{q} = {n} мало! Нужно N >= {MIN_N}")
                print(f"     Подсказка: P=3, Q=11 → N=33  или  P=5, Q=7 → N=35")
                continue
            break

        phi = (p - 1) * (q - 1)
        print(f"  N = {p}×{q} = {n}  ✅")
        print(f"  φ(N) = ({p}-1)×({q}-1) = {phi}")

        e = 2
        while gcd(e, phi) != 1 or e >= phi:
            e = sympy.randprime(3, phi)
        print(f"  E = {e}  (автовыбор, НОД(E, φ(N))=1)")

        d = eq(e, 1, phi)
        print(f"  D = {d}  (секретный ключ, E×D mod φ(N) = {(e*d) % phi})")
        print(f"  Открытый ключ: (E={e}, N={n})")

        h = hash_quad(text, n)
        print(f"\n  Хеш: m = h('{text}') = {h}")
        s = pow(h, d, n)
        print(f"  Подпись: S = m^D mod N = {h}^{d} mod {n} = {s}")
        print(f"\n  ✉ Отправить: сообщение + S={s}, E={e}, N={n}")

    if operation == 2:
        while True:
            n = int(input("  Введите N: "))
            if n < MIN_N:
                print(f"  ❌ N={n} мало! Нужно N >= {MIN_N}"); continue
            break
        s = int(input("  Введите S (подпись): "))
        e = int(input("  Введите E: "))

        h        = hash_quad(text, n)
        h_from_s = pow(s, e, n)

        print(f"\n  Хеш сообщения:       m' = h('{text}') = {h}")
        print(f"  Расшифровка подписи: m  = S^E mod N = {s}^{e} mod {n} = {h_from_s}")

        if h == h_from_s:
            print("  ✅ ПОДПИСЬ ВЕРНА")
        else:
            print("  ❌ ПОДПИСЬ НЕВЕРНА")


# ─────────────────────────────────────────────
#  ELGAMAL ЦИФРОВАЯ ПОДПИСЬ
# ─────────────────────────────────────────────

def ElGamal(operation, text):
    print("\n── ELGAMAL ЦИФРОВАЯ ПОДПИСЬ ──")

    while True:
        p = int(input("  Введите P (простое, >= 37): "))
        if not is_prime(p):
            print("  ❌ P должно быть простым!"); continue
        if p < 37:
            print(f"  ❌ P={p} мало! Нужно P >= 37")
            print(f"     Подсказка: минимум P=37")
            continue
        break

    g = int(input(f"  Введите G (1 < G < {p}): "))
    if not (1 < g < p):
        print("  ❌ G должно быть 1 < G < P!"); return

    phi = p - 1
    valid_k = [k for k in range(2, min(p, 100)) if gcd(k, phi) == 1]
    print(f"\n  Допустимые K (НОД(K, φ(P)={phi})=1):")
    print(f"  {valid_k}")

    if operation == 1:
        x = int(input(f"\n  Введите X — секретный ключ (1 < X < {p - 1}): "))
        if not (1 < x < p - 1):
            print("  ❌ X вне диапазона!"); return

        y = pow(g, x, p)
        print(f"  Y = G^X mod P = {g}^{x} mod {p} = {y}  (открытый ключ)")

        m = hash_quad(text, phi)
        print(f"  Хеш: m = h('{text}') mod {phi} = {m}")

        # Выбираем K и пересчитываем пока B = 0 (защита от уязвимости)
        attempts = 0
        while True:
            k = 2
            while gcd(k, phi) != 1 or k >= p - 1:
                k = sympy.randprime(3, p - 2)

            a = pow(g, k, p)
            b = comparisons(k, (m - x * a) % phi, phi)

            if b == 0:
                attempts += 1
                print(f"  ⚠️  B=0 — уязвимость! K={k} не подходит, выбираем новый K... (попытка {attempts})")
                continue
            break

        print(f"\n  K = {k}  (рандомизатор)")
        print(f"  A = G^K mod P = {g}^{k} mod {p} = {a}")
        print(f"  B = K⁻¹*(m - X*A) mod (P-1) = {b}")
        print(f"\n  ✉ Подпись: (A={a}, B={b}),  Y={y}")

    if operation == 2:
        sig_input = input("\n  Введите подпись A B (через пробел): ").split()
        a, b = int(sig_input[0]), int(sig_input[1])

        # ЗАЩИТА: проверяем что A и B не нулевые
        if a <= 0 or a >= p:
            print(f"  ❌ A={a} вне диапазона (0 < A < {p})! Подпись отклонена."); return
        if b == 0:
            print(f"  ❌ B=0 — недопустимое значение! Подпись отклонена.")
            print(f"     Причина: при B=0 подпись не зависит от сообщения (уязвимость).")
            return

        y = int(input("  Введите Y (открытый ключ): "))
        m = hash_quad(text, phi)
        print(f"  Хеш: m = h('{text}') mod {phi} = {m}")

        v1 = (pow(y, a, p) * pow(a, b, p)) % p
        v2 = pow(g, m, p)

        print(f"\n  V1 = Y^A * A^B mod P = {pow(y,a,p)} * {pow(a,b,p)} mod {p} = {v1}")
        print(f"  V2 = G^m mod P = {g}^{m} mod {p} = {v2}")

        if v1 == v2:
            print("  ✅ ПОДПИСЬ ВЕРНА")
        else:
            print("  ❌ ПОДПИСЬ НЕВЕРНА")


# ─────────────────────────────────────────────
#                 ГЛАВНОЕ МЕНЮ
# ─────────────────────────────────────────────

while True:
    print("""
╔══════════════════════════════════╗
║  Выберите алгоритм ЦП:           ║
║   1. RSA     — цифровая подпись  ║
║   2. ElGamal — цифровая подпись  ║
║   3. Выход                       ║
╚══════════════════════════════════╝""")

    select: int = int(input(">> "))
    if select == 3: sys.exit()
    if select not in [1, 2]:
        print("  Неверный выбор!"); continue

    print("""
  Выберите действие:
    1. Подписать
    2. Проверить подпись""")

    operation: int = int(input(">> "))
    if operation not in [1, 2]:
        print("  Неверный выбор!"); continue

    text: str = input("Введите текст: ").strip().lower()
    print()

    for ch, code_r in [(".", "тчк"), (",", "зпт"), (" ", "прб")]:
        text = text.replace(ch, code_r)

    if select == 1: RSA(operation, text); print()
    if select == 2: ElGamal(operation, text); print()
