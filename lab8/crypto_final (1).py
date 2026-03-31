import sympy
import sys
from typing import List
from math import gcd

# Алфавит по методичке: 31 буква (без Ё и Й)
alphabet: str = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

# Алфавит из таблицы 1 задания (без Ё, Й — 31 символ)
task_alphabet = "абвгдежзиклмнопрстуфхцчшщъыьэюя"  # без й

# ─────────────────────────────────────────────
#              ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────

def euclid(a: int, b: int):
    res: List[int] = []
    while a != 0 and b != 0:
        if a > b:
            res.append(a // b); a %= b
        else:
            res.append(b // a); b %= a
    return res

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d**2 <= n and n % d != 0: d += 2
    return d**2 > n

def euler_func(num):
    return sum(1 for k in range(1, num + 1) if gcd(num, k) == 1)

def eq(a: int, b: int, m: int) -> int:
    q: List[int] = euclid(a, m)
    if m < a: q.insert(0, 0)
    p: List = [1, q[0]]
    for i in range(1, len(q)):
        p.append(p[i] * q[i] + p[i - 1])
    return ((-1)**(len(q) - 1) * p[-2] * b) % m

def mod_inv(a: int, p: int) -> int:
    return pow(a, p - 2, p)

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
    return int(((-1)**(n - 1) * p[-2] * b) % m)

def simple_hash(text: str, mod: int) -> int:
    s = sum(task_alphabet.index(ch) + 1 if ch in task_alphabet else ord(ch) for ch in text)
    return (s % (mod - 1)) + 1

def digitization(open_text: str) -> List[int]:
    return [task_alphabet.index(ch) + 1 for ch in open_text]

def decryption_format(dec_text: str) -> str:
    dec_text = dec_text.replace("тчк", ".").replace("зпт", ",").replace("прб", " ")
    result = list(dec_text[0].upper() + dec_text[1:])
    for i in range(len(result) - 3):
        if result[i] == ".": result[i + 2] = result[i + 2].upper()
    return "".join(result)

def encode_text(text: str) -> str:
    for ch, code in [(".", "тчк"), (",", "зпт"), (" ", "прб")]:
        text = text.replace(ch, code)
    return text

def El_Gamal_key_generate(phi: int) -> int:
    key = 0
    while gcd(key, phi) != 1: key = sympy.randprime(3, phi)
    return key

# ─────────────────────────────────────────────
#              ECC ВСПОМОГАТЕЛЬНЫЕ
# ─────────────────────────────────────────────

def point_add(P, Q, a: int, p: int):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = int(P[0]), int(P[1])
    x2, y2 = int(Q[0]), int(Q[1])
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if x1 == x2 and y1 == y2:
        if y1 == 0: return None
        lam = (3 * x1**2 + a) * mod_inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * mod_inv(x2 - x1, p) % p
    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return [int(x3), int(y3)]

def composition(point, k: int, a: int, p: int):
    result = None
    addend = [int(point[0]), int(point[1])]
    while k:
        if k & 1: result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    if result is None: return False
    return [result[0], result[1]]

# ─────────────────────────────────────────────
#  БЛОК H: АСИММЕТРИЧНЫЕ ШИФРЫ
# ─────────────────────────────────────────────

def RSA_cipher(operation, text):
    print("\n── RSA ШИФРОВАНИЕ ──")
    max_index = len(task_alphabet)  # 31
    if operation == 1:
        while True:
            p = int(input("  Введите P (простое): "))
            q = int(input("  Введите Q (простое): "))
            if not is_prime(p) or not is_prime(q):
                print("  ❌ P и Q должны быть простыми!")
                continue
            n = p * q
            if n <= max_index:
                print(f"  ❌ N = {p}×{q} = {n} слишком мало!")
                print(f"     Нужно N > {max_index} (размер алфавита)")
                print(f"     Подсказка: попробуйте P={5}, Q={7} → N=35")
                continue
            break
        phi = (p - 1) * (q - 1)
        print(f"  N = {p}×{q} = {n}  ✅ (N > {max_index})")
        print(f"  φ(N) = ({p}-1)×({q}-1) = {phi}")
        e = int(input(f"  Введите E (1 < E < {phi}, взаимно простое с φ(N)): "))
        while gcd(e, phi) != 1 or e >= phi or e <= 1:
            print(f"  ❌ E не взаимно просто с φ(N)={phi}, автовыбор...")
            e = sympy.randprime(3, phi)
        print(f"  E = {e}  ✅")
        d = eq(e, 1, phi)
        print(f"  D = {d}  (секретный ключ)")
        print(f"  Открытый ключ:  (E={e}, N={n})")
        digit_text = digitization(text)
        ciphertext = [pow(m, e, n) for m in digit_text]
        print("  Зашифрованный текст:", " ".join(map(str, ciphertext)))

    if operation == 2:
        while True:
            n = int(input("  Введите N: "))
            if n <= max_index:
                print(f"  ❌ N={n} слишком мало! Нужно N > {max_index}")
                continue
            break
        d = int(input("  Введите D: "))
        pairs = list(map(int, text.split()))
        result_text = "".join(task_alphabet[pow(c, d, n) - 1] for c in pairs)
        print("  Расшифрованный текст:", decryption_format(result_text))


def get_valid_k_list(phi: int, p: int) -> list:
    """Возвращает все допустимые k: 1 < k < p, НОД(k, phi) = 1"""
    return [k for k in range(2, p) if gcd(k, phi) == 1]


def ElGamal_cipher(operation, text):
    print("\n── ELGAMAL ШИФРОВАНИЕ ──")
    max_index = len(task_alphabet)  # 31

    # Ввод и проверка p
    while True:
        p = int(input("  Введите p (простое): "))
        if not is_prime(p):
            print("  ❌ p должно быть простым!"); continue
        if p <= max_index:
            print(f"  ❌ p={p} слишком мало! Нужно p > {max_index}")
            print(f"     Минимум: p = 37"); continue
        break

    phi = p - 1
    valid_k = get_valid_k_list(phi, p)
    print(f"  ✅ p={p}, φ(p)={phi}")
    print(f"  Допустимые значения k (НОД(k,{phi})=1, 1<k<{p}):")
    print(f"  {valid_k}")

    g = int(input(f"  Введите g (1 < g < {p}): "))
    if not (1 < g < p):
        print("  ❌ g вне диапазона!"); return

    if operation == 1:
        x = int(input(f"  Введите x — секретный ключ (1 < x < {p}): "))
        if not (1 < x < p):
            print("  ❌ x вне диапазона!"); return
        y = pow(g, x, p)
        print(f"  y = {g}^{x} mod {p} = {y}")
        print(f"  Открытые ключи: p={p}, g={g}, y={y}")
        print(f"  Секретный ключ: x={x}")

        digit_text = digitization(text)
        result_text = []
        print("\n  Шифрование по символам:")
        for i, mi in enumerate(digit_text):
            print(f"    Символ '{task_alphabet[mi-1]}' (m={mi})")
            print(f"    Допустимые k: {valid_k}")
            k = int(input(f"    Введите k[{i+1}]: "))
            while k not in valid_k:
                print(f"    ❌ k={k} не подходит! Выбери из: {valid_k}")
                k = int(input(f"    Введите k[{i+1}]: "))
            a_i = pow(g, k, p)
            b_i = (pow(y, k, p) * mi) % p
            print(f"    ✅ a = g^k mod p = {g}^{k} mod {p} = {a_i}")
            print(f"       b = y^k * m mod p = {y}^{k} * {mi} mod {p} = {b_i}")
            result_text.extend([a_i, b_i])
        print("\n  Зашифрованный текст:", " ".join(map(str, result_text)))

    if operation == 2:
        x = int(input("  Введите x — секретный ключ: "))
        pairs = list(map(int, text.split()))
        result = ""
        print("\n  Расшифровка пар (a, b):")
        for i in range(0, len(pairs) - 1, 2):
            a_i, b_i = pairs[i], pairs[i + 1]
            m = comparisons(a_i**x % p, b_i, p)
            print(f"    a={a_i}, b={b_i} → m={m} ('{task_alphabet[m-1]}')")
            result += task_alphabet[m - 1]
        print("  Расшифрованный текст:", decryption_format(result))


def ECC_cipher(operation, text):
    print("\n── ECC ШИФРОВАНИЕ (абсцисса точки) ──")
    print("  Параметры кривой E_p(a,b): y² = x³ + ax + b mod p")
    a   = int(input("  a   = "))
    b   = int(input("  b   = "))
    p_m = int(input("  p   = "))
    gx  = int(input("  Gx  = "))
    gy  = int(input("  Gy  = "))
    g   = [gx, gy]
    c_b = int(input("  C_b = "))
    q_m = int(input("  q_m = "))

    if operation == 1:
        k   = int(input("  k   = "))
        m   = int(input("  m   = "))   # ← просто вводишь 10

        if not (0 < k < q_m):
            print("  k вне диапазона!"); return
        if not (0 < m < p_m):
            print(f"  m должно быть 0 < m < p={p_m}!"); return

        d_b  = composition(g, c_b, a, p_m)
        R    = composition(g, k, a, p_m)
        P_pt = composition(d_b, k, a, p_m)
        e    = (m * P_pt[0]) % p_m

        print(f"\n  D_b = [{c_b}]*G    = {d_b}  (открытый ключ получателя)")
        print(f"  R   = [{k}]*G    = {R}")
        print(f"  P   = [{k}]*D_b  = {P_pt}")
        print(f"  e   = m * x mod p = {m} * {P_pt[0]} mod {p_m} = {e}")
        print(f"\n  ✉ Шифртекст: (R, e) = ({R}, {e})")

    if operation == 2:
        # Вводим шифртекст как: Rx Ry e  (через пробел, например: 10 6 5)
        print("  Введите шифртекст в формате:  Rx Ry e  (через пробел)")
        parts = list(map(int, input("  Шифртекст: ").split()))
        if len(parts) < 3:
            print("  Нужно 3 числа!"); return
        R_in  = [parts[0], parts[1]]
        e_val = parts[2]

        Q     = composition(R_in, c_b, a, p_m)
        x_inv = pow(Q[0], p_m - 2, p_m)
        m_out = (e_val * x_inv) % p_m

        print(f"\n  Q = [{c_b}]*R = [{c_b}]*{R_in} = {Q}")
        print(f"  x⁻¹ = {Q[0]}^(p-2) mod {p_m} = {x_inv}")
        print(f"  m = e * x⁻¹ mod p = {e_val} * {x_inv} mod {p_m} = {m_out}")

        if 1 <= m_out <= len(task_alphabet):
            print(f"\n  ✅ Расшифровано: m = {m_out}  →  буква '{task_alphabet[m_out-1].upper()}'")
        else:
            print(f"\n  ✅ Расшифровано: m = {m_out}")

# ─────────────────────────────────────────────
#  БЛОК I: ЦИФРОВЫЕ ПОДПИСИ
# ─────────────────────────────────────────────

def RSA_sign(operation, text):
    print("\n── RSA ЦИФРОВАЯ ПОДПИСЬ ──")
    p = int(input("  P = ")); q = int(input("  Q = "))
    if not is_prime(p) or not is_prime(q):
        print("  P и Q должны быть простыми!"); return
    n = p * q; phi = (p - 1) * (q - 1)
    print(f"  N={n}, φ(N)={phi}")
    e = int(input(f"  E (1 < E < {phi}): "))
    while gcd(e, phi) != 1 or e >= phi or e <= 1:
        print("  Автовыбор E..."); e = sympy.randprime(3, phi)
    d = eq(e, 1, phi)
    print(f"  D={d}  |  Открытый ключ: (E={e}, N={n})")

    if operation == 1:
        m = simple_hash(text, n)
        S = pow(m, d, n)
        print(f"  Хеш: m = h('{text}') = {m}")
        print(f"  S = m^D mod N = {m}^{d} mod {n} = {S}")
        print(f"\n  ✉ Подпись S = {S}")

    if operation == 2:
        S = int(input("  S = "))
        m_check = simple_hash(text, n)
        m_dec   = pow(S, e, n)
        print(f"  m' (хеш) = {m_check}")
        print(f"  m  (из S) = S^E mod N = {m_dec}")
        print("  ✅ ПОДПИСЬ ВЕРНА" if m_check == m_dec else "  ❌ ПОДПИСЬ НЕВЕРНА")


def ElGamal_sign(operation, text):
    print("\n── ELGAMAL ЦИФРОВАЯ ПОДПИСЬ ──")
    P = int(input("  P = "))
    if not is_prime(P): print("  P должно быть простым!"); return
    G = int(input(f"  G = "))

    if operation == 1:
        X = int(input(f"  X (секретный ключ, 1 < X < {P-1}): "))
        Y = pow(G, X, P)
        print(f"  Y = G^X mod P = {Y}  (открытый ключ)")
        m = simple_hash(text, P)
        print(f"  Хеш: m = {m}")
        K = int(input(f"  K (1 < K < {P-1}, НОД(K,{P-1})=1): "))
        while gcd(K, P - 1) != 1 or K <= 1 or K >= P - 1:
            print("  K не подходит!"); K = int(input("  K = "))
        R     = pow(G, K, P)
        K_inv = eq(K, 1, P - 1)
        S     = (K_inv * (m - X * R)) % (P - 1)
        print(f"  R = {R},  K⁻¹ = {K_inv},  S = {S}")
        print(f"\n  ✉ Подпись: (R={R}, S={S})")

    if operation == 2:
        X  = int(input("  X (секретный ключ): "))
        Y  = pow(G, X, P)
        R  = int(input("  R = ")); S = int(input("  S = "))
        if not (0 < R < P): print("  ❌ R вне диапазона"); return
        m  = simple_hash(text, P)
        V1 = (pow(Y, R, P) * pow(R, S, P)) % P
        V2 = pow(G, m, P)
        print(f"  V1 = Y^R * R^S mod P = {V1}")
        print(f"  V2 = G^m mod P = {V2}")
        print("  ✅ ПОДПИСЬ ВЕРНА" if V1 == V2 else "  ❌ ПОДПИСЬ НЕВЕРНА")


# ─────────────────────────────────────────────
#                 ГЛАВНОЕ МЕНЮ
# ─────────────────────────────────────────────

while True:
    print("""
╔═══════════════════════════════════════╗
║  БЛОК H: АСИММЕТРИЧНЫЕ ШИФРЫ          ║
║   1. RSA       — шифрование           ║
║   2. ElGamal   — шифрование           ║
║   3. ECC       — шифрование           ║
╠═══════════════════════════════════════╣
║  БЛОК И: ЦИФРОВЫЕ ПОДПИСИ             ║
║   4. RSA       — цифровая подпись     ║
║   5. ElGamal   — цифровая подпись     ║
╠═══════════════════════════════════════╣
║   0. Выход                            ║
╚═══════════════════════════════════════╝""")

    select = int(input(">> "))
    if select == 0: sys.exit()
    if select not in [1, 2, 3, 4, 5]:
        print("Неверный выбор!"); continue

    if select in [1, 2, 3]:
        print("\n  1. Шифрование\n  2. Расшифровка")
    else:
        print("\n  1. Подписать\n  2. Проверить подпись")

    operation = int(input(">> "))
    if operation not in [1, 2]:
        print("Неверный выбор!"); continue

    # ECC принимает числа, не текст — обрабатываем отдельно
    if select == 3:
        text = ""
    else:
        text = input("Введите текст: ").strip().lower()
        if select in [1, 2] and operation == 1:
            text = encode_text(text)

    if   select == 1: RSA_cipher(operation, text)
    elif select == 2: ElGamal_cipher(operation, text)
    elif select == 3: ECC_cipher(operation, text)
    elif select == 4: RSA_sign(operation, text)
    elif select == 5: ElGamal_sign(operation, text)
    print()
