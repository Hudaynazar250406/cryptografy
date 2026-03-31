#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
КУЗНЕЧИК (Grasshopper) — ГОСТ Р 34.12-2015
Блок: 128 бит, Ключ: 256 бит, 10 раундов
Тест по контрольному примеру А.1 из ГОСТ Р 34.12-2015
"""

import sys

# ══════════════════════════════════════════════════════════════
# S-блок (π) и обратный — ГОСТ Р 34.12-2015, раздел 4.1.1
# ══════════════════════════════════════════════════════════════
PI = [
    252,238,221, 17,207,110, 49, 22,251,196,250,218, 35,197,  4, 77,
    233,119,240,219,147, 46,153,186, 23, 54,241,187, 20,205, 95,193,
    249, 24,101, 90,226, 92,239, 33,129, 28, 60, 66,139,  1,142, 79,
      5,132,  2,174,227,106,143,160,  6, 11,237,152,127,212,211, 31,
    235, 52, 44, 81,234,200, 72,171,242, 42,104,162,253, 58,206,204,
    181,112, 14, 86,  8, 12,118, 18,191,114, 19, 71,156,183, 93,135,
     21,161,150, 41, 16,123,154,199,243,145,120,111,157,158,178,177,
     50,117, 25, 61,255, 53,138,126,109, 84,198,128,195,189, 13, 87,
    223,245, 36,169, 62,168, 67,201,215,121,214,246,124, 34,185,  3,
    224, 15,236,222,122,148,176,188,220,232, 40, 80, 78, 51, 10, 74,
    167,151, 96,115, 30,  0, 98, 68, 26,184, 56,130,100,159, 38, 65,
    173, 69, 70,146, 39, 94, 85, 47,140,163,165,125,105,213,149, 59,
      7, 88,179, 64,134,172, 29,247, 48, 55,107,228,136,217,231,137,
    225, 27,131, 73, 76, 63,248,254,141, 83,170,144,202,216,133, 97,
     32,113,103,164, 45, 43,  9, 91,203,155, 37,208,190,229,108, 82,
     89,166,116,210,230,244,180,192,209,102,175,194, 57, 75, 99,182,
]

PI_INV = [0] * 256
for i, v in enumerate(PI):
    PI_INV[v] = i

# ══════════════════════════════════════════════════════════════
# Умножение в GF(2^8), модуль p(x) = x^8+x^7+x^6+x+1 = 0x1C3
# ══════════════════════════════════════════════════════════════
GF_MOD = 0x1C3

def gf_mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a & 0x100:
            a ^= GF_MOD
        b >>= 1
    return result

# ══════════════════════════════════════════════════════════════
# Коэффициенты линейного преобразования l — ГОСТ 4.1.2
# ══════════════════════════════════════════════════════════════
L_COEFFS = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]

def l_func(a):
    """l(a15..a0) = сумма коэф_i * a_i в GF(2^8)"""
    result = 0
    for i in range(16):
        result ^= gf_mul(L_COEFFS[i], a[i])
    return result

# ══════════════════════════════════════════════════════════════
# Базовые преобразования X, S, R, L и обратные
# Блок = список из 16 байт [a15, a14, ..., a0]
# ══════════════════════════════════════════════════════════════

def X(k, a):
    """X[k](a) = k XOR a"""
    return [k[i] ^ a[i] for i in range(16)]

def S(a):
    """Нелинейная подстановка — применяем S-блок к каждому байту"""
    return [PI[b] for b in a]

def S_inv(a):
    """Обратная нелинейная подстановка"""
    return [PI_INV[b] for b in a]

def R(a):
    """R(a15||..||a0) = l(a15,..a0) || a15 || .. || a1"""
    new_byte = l_func(a)
    return [new_byte] + a[:-1]

def R_inv(a):
    """R^{-1}(a15||..||a0) = a14||..||a0||l(a14,..a0,a15)"""
    tail = a[1:] + [a[0]]
    new_byte = l_func(tail)
    return a[1:] + [new_byte]

def L(a):
    """L(a) = R^16(a)"""
    for _ in range(16):
        a = R(a)
    return a

def L_inv(a):
    """L^{-1}(a) = (R^{-1})^16(a)"""
    for _ in range(16):
        a = R_inv(a)
    return a

# ══════════════════════════════════════════════════════════════
# Итерационные константы C_i = L(i), i = 1..32
# ══════════════════════════════════════════════════════════════

def _gen_constants():
    consts = []
    for i in range(1, 33):
        consts.append(L([0] * 15 + [i]))
    return consts

ITER_CONSTS = _gen_constants()

# ══════════════════════════════════════════════════════════════
# Развёртка ключа — F[k](a1,a0) и key_schedule
# ══════════════════════════════════════════════════════════════

def F(k, a1, a0):
    """F[k](a1,a0) = (LSX[k](a1) XOR a0, a1)"""
    lsx = L(S(X(k, a1)))
    return X(lsx, a0), a1

def key_schedule(key_bytes):
    """256-битный ключ → 10 раундовых ключей K1..K10"""
    k1 = list(key_bytes[:16])
    k2 = list(key_bytes[16:])
    keys = [k1, k2]
    a, b = k1[:], k2[:]
    for i in range(4):
        for j in range(8):
            a, b = F(ITER_CONSTS[8 * i + j], a, b)
        keys.append(a[:])
        keys.append(b[:])
    return keys  # K1..K10

# ══════════════════════════════════════════════════════════════
# Шифрование и расшифрование одного блока (16 байт)
# ══════════════════════════════════════════════════════════════

def encrypt_block(plain_bytes, round_keys):
    """9 раундов LSX + финальный X"""
    a = list(plain_bytes)
    for i in range(9):
        a = L(S(X(round_keys[i], a)))
    return bytes(X(round_keys[9], a))

def decrypt_block(cipher_bytes, round_keys):
    """Обратный X + 9 обратных раундов X·S^{-1}·L^{-1}"""
    a = list(cipher_bytes)
    a = X(round_keys[9], a)
    for i in range(8, -1, -1):
        a = X(round_keys[i], S_inv(L_inv(a)))
    return bytes(a)

# ══════════════════════════════════════════════════════════════
# ECB режим
# use_padding=True  — PKCS#7 (для произвольных данных)
# use_padding=False — без padding (для контрольных примеров ГОСТ)
# ══════════════════════════════════════════════════════════════

def _pkcs7_pad(data, block=16):
    n = block - len(data) % block
    return data + bytes([n] * n)

def _pkcs7_unpad(data):
    n = data[-1]
    if n < 1 or n > 16:
        raise ValueError("Некорректный padding")
    return data[:-n]

def encrypt_ecb(data, key_bytes, use_padding=True):
    rk = key_schedule(key_bytes)
    if use_padding:
        data = _pkcs7_pad(data)
    else:
        if len(data) % 16 != 0:
            raise ValueError("Длина данных должна быть кратна 16 байтам (или используйте use_padding=True)")
    return b''.join(encrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))

def decrypt_ecb(data, key_bytes, use_padding=True):
    if len(data) % 16 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 16 байтам")
    rk = key_schedule(key_bytes)
    dec = b''.join(decrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))
    return _pkcs7_unpad(dec) if use_padding else dec

# ══════════════════════════════════════════════════════════════
# Русский алфавит — 32 буквы, нумерация 1..32
# ══════════════════════════════════════════════════════════════
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
L2N = {c: i+1 for i, c in enumerate(ALPHABET)}
N2L = {i+1: c for i, c in enumerate(ALPHABET)}

def preprocess(text):
    """Предобработка: нижний регистр, замена знаков, удаление пробелов"""
    res = []
    for ch in text.lower():
        if ch == ' ':
            continue
        elif ch == ',':
            res.append('зпт')
        elif ch == '.':
            res.append('тчк')
        elif ch in ALPHABET:
            res.append(ch)
    return ''.join(res)

def postprocess(text):
    """Обратная замена: зпт → , тчк → ."""
    return text.replace('зпт', ',').replace('тчк', '.')

def text_to_bytes_ru(text):
    return bytes([L2N[c] for c in text])

def bytes_to_text_ru(data):
    result = []
    for b in data:
        if 1 <= b <= 32:
            result.append(N2L[b])
    return ''.join(result)

def encrypt_russian(plain, key_hex):
    processed = preprocess(plain)
    if not processed:
        raise ValueError("Текст пуст после предобработки")
    data = text_to_bytes_ru(processed)
    key  = bytes.fromhex(key_hex)
    enc  = encrypt_ecb(data, key, use_padding=True)
    return enc.hex().upper()

def decrypt_russian(cipher_hex, key_hex):
    key = bytes.fromhex(key_hex)
    enc = bytes.fromhex(cipher_hex)
    dec = decrypt_ecb(enc, key, use_padding=True)
    return bytes_to_text_ru(dec)

# ══════════════════════════════════════════════════════════════
# ТЕСТ ПО ГОСТ Р 34.12-2015 (Приложение А.1)
# ══════════════════════════════════════════════════════════════

def run_gost_test():
    print("=" * 65)
    print("  ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.1 (КУЗНЕЧИК)")
    print("=" * 65)

    KEY   = bytes.fromhex(
        "8899aabbccddeeff0011223344556677"
        "fedcba98765432100123456789abcdef"
    )
    PLAIN    = bytes.fromhex("1122334455667700ffeeddccbbaa9988")
    EXPECTED = "7f679d90bebc24305a468d42b9d4edcd"

    # Ожидаемые раундовые ключи из ГОСТ А.1.4
    EXP_KEYS = [
        "8899aabbccddeeff0011223344556677",
        "fedcba98765432100123456789abcdef",
        "db31485315694343228d2b3bef05d129",
        "57646468c44a5e28d3e59246f429f1ac",
        "bd079435165c6432b532e82834da581b",
        "51e640757e8745de705727265a0098b1",
        "5a7925017b9fdd3ed72a91a22286f984",
        "bb44e25378c73123a5f32f73cdb6e517",
        "72e9dd7416bcf45b755dbaa88e4a4043",
    ]

    rk = key_schedule(KEY)

    print("── Раундовые ключи K1..K9 (сравнение с ГОСТ А.1.4) ──")
    for i in range(9):
        kh  = bytes(rk[i]).hex()
        exp = EXP_KEYS[i]
        ok  = '✅' if kh == exp else '❌'
        print(f"  K{i+1:2d}: {kh}  {ok}")
    print(f"  K10: {bytes(rk[9]).hex()}")

    # Промежуточные шаги А.1.5
    print("── Промежуточные шаги (А.1.5) ──")
    EXP_STEPS = [
        ("X[K1](a)",    "99bb99ff99bb99ffffffffffffffffff"),
        ("S(X[K1](a))", "e87de8b6e87de8b6b6b6b6b6b6b6b6b6"),
        ("LSX[K1](a)",  "e297b686e355b0a1cf4a2f9249140830"),
    ]
    a  = list(PLAIN)
    xk = X(rk[0], a)
    sx = S(xk)
    lsx = L(sx)
    steps = [bytes(xk).hex(), bytes(sx).hex(), bytes(lsx).hex()]
    for (name, exp), got in zip(EXP_STEPS, steps):
        ok = '✅' if got == exp else '❌'
        print(f"  {name:<18}: {got}  {ok}")

    # Финальный тест шифрования/расшифрования
    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc,   rk)

    print(f"── Шифрование блока ──")
    print(f"  Открытый : {PLAIN.hex()}")
    print(f"  Ожидается: {EXPECTED}")
    print(f"  Получено : {enc.hex()}")
    print(f"  Результат: {'✅ ВЕРНО' if enc.hex() == EXPECTED else '❌ ОШИБКА'}")
    print(f"── Расшифрование блока ──")
    print(f"  Шифртекст: {enc.hex()}")
    print(f"  Получено : {dec.hex()}")
    print(f"  Результат: {'✅ ВЕРНО' if dec == PLAIN else '❌ ОШИБКА'}")

    # Тест >1000 байт
    print(f"── Тест на тексте >1000 байт ──")
    long_text = b"Kuznyechik GOST R 34.12-2015 block cipher test data. " * 20
    enc2 = encrypt_ecb(long_text, KEY, use_padding=True)
    dec2 = decrypt_ecb(enc2,      KEY, use_padding=True)
    ok2  = dec2 == long_text
    print(f"  Длина       : {len(long_text)} байт")
    print(f"  Зашифровано : {len(enc2)} байт")
    print(f"  Расшифровано: {'✅ Совпадает' if ok2 else '❌ Не совпадает'}")
    print(f"  Шифртекст   : {enc2.hex()[:64]}...")

# ══════════════════════════════════════════════════════════════
# ГЛАВНОЕ МЕНЮ
# ══════════════════════════════════════════════════════════════

def get_key(prompt="Ключ (64 hex, Enter=тестовый): "):
    kh = input(prompt).strip().replace(' ', '')
    if not kh:
        kh = "8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"
        print(f"  Используется тестовый ключ: {kh}")
    if len(kh) != 64 or not all(c in '0123456789abcdefABCDEF' for c in kh):
        raise ValueError("Ключ должен содержать ровно 64 hex-символа")
    return kh

def main():
    print("╔" + "═" * 63 + "╗")
    print("║{:^63}║".format("КУЗНЕЧИК — ГОСТ Р 34.12-2015"))
    print("╚" + "═" * 63 + "╝")

    while True:
        print("МЕНЮ:")
        print("  1. Тест по ГОСТ Р 34.12-2015 (А.1)")
        print("  2. Шифрование  (русский текст)")
        print("  3. Расшифрование (русский текст)")
        print("  4. Шифрование  (hex данные / контрольные примеры)")
        print("  5. Расшифрование (hex данные)")
        print("  0. Выход")
        ch = input("Выбор: ").strip()

        if ch == "0":
            print("До свидания!")
            sys.exit(0)

        elif ch == "1":
            run_gost_test()

        elif ch == "2":
            try:
                kh  = get_key()
                txt = input("Текст (русские буквы): ").strip()
                enc = encrypt_russian(txt, kh)
                print(f"Шифртекст (hex): {enc}")
                save = input("Сохранить в файл? (y/n): ").strip().lower()
                if save == 'y':
                    fn = input("Имя файла (kuz_cipher.bin): ").strip() or "kuz_cipher.bin"
                    open(fn, 'wb').write(bytes.fromhex(enc))
                    print(f"✅ Сохранено в '{fn}'")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif ch == "3":
            try:
                kh   = get_key()
                chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                dec  = decrypt_russian(chex, kh)
                print(f"Расшифрованный текст: {dec}")
                r = input("Восстановить знаки препинания? (y/n): ").strip().lower()
                if r == 'y':
                    print(f"С пунктуацией: {postprocess(dec)}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif ch == "4":
            try:
                kh   = get_key()
                phex = input("Открытый текст (hex): ").strip().replace(' ', '')
                pb   = bytes.fromhex(phex)
                # Без padding — для контрольных примеров ГОСТ (длина кратна 16)
                # С padding  — для произвольных данных
                if len(pb) % 16 == 0:
                    enc = encrypt_ecb(pb, bytes.fromhex(kh), use_padding=False)
                else:
                    print("  Длина не кратна 16 — будет применён PKCS#7 padding")
                    enc = encrypt_ecb(pb, bytes.fromhex(kh), use_padding=True)
                print(f"Шифртекст (hex): {enc.hex().upper()}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif ch == "5":
            try:
                kh   = get_key()
                chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                cb   = bytes.fromhex(chex)
                # Спрашиваем — был ли padding при шифровании
                p = input("При шифровании использовался padding? (y/n): ").strip().lower()
                use_p = (p == 'y')
                dec = decrypt_ecb(cb, bytes.fromhex(kh), use_padding=use_p)
                print(f"Открытый текст (hex): {dec.hex().upper()}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")

        else:
            print("❌ Неверный выбор!")


if __name__ == "__main__":
    main()
