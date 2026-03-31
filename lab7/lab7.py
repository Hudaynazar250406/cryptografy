#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МАГМА (ГОСТ Р 34.12-2015 / ГОСТ 28147-89)
Тест по контрольному примеру из ГОСТ Р 34.12-2015 Приложение А.2
"""
import sys

# ═══ ТАБЛИЦА ПОДСТАНОВОК (pi) из ГОСТ Р 34.12-2015, раздел 5.1.1 ═══
# 8 строк по 16 значений (4 бита → 4 бита)
PI = [
    [12,4,6,2,10,5,11,9,14,8,13,7,0,3,15,1],   # pi_0
    [6,8,2,3,9,10,5,12,1,14,4,7,11,13,0,15],    # pi_1
    [11,3,5,8,2,15,10,13,14,1,7,4,12,9,6,0],    # pi_2
    [12,8,2,1,13,4,15,6,7,0,10,5,3,14,9,11],    # pi_3
    [7,15,5,10,8,1,6,13,0,9,3,14,11,4,2,12],    # pi_4
    [5,13,15,6,9,2,12,10,11,7,8,1,4,3,14,0],    # pi_5
    [8,14,2,5,6,9,1,12,15,4,11,0,13,10,3,7],    # pi_6
    [1,7,14,13,0,5,8,3,4,15,10,6,9,12,11,2],    # pi_7
]

def t(a):
    """Нелинейная подстановка t(a): 8 тетрад по 4 бита"""
    result = 0
    for i in range(8):
        nibble = (a >> (4*i)) & 0xF
        result |= PI[i][nibble] << (4*i)
    return result

def rot11(x):
    """Циклический сдвиг 32-битного числа влево на 11"""
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k, a):
    """g[k](a) = rot11(t(a ⊞ k))"""
    return rot11(t((a + k) & 0xFFFFFFFF))

def key_schedule(key_bytes):
    """256-битный ключ → 32 подключа"""
    # Читаем как 8 слов по 32 бита (little-endian)
    k = [int.from_bytes(key_bytes[4*i:4*i+4], 'little') for i in range(8)]
    # K1..K24: k0..k7 повторить 3 раза; K25..K32: k7..k0
    return k * 3 + k[::-1]

def encrypt_block(blk, rk):
    """Зашифрование 8-байтового блока"""
    # a = (a_1, a_0) — старшая и младшая половины
    a1 = int.from_bytes(blk[4:], 'little')
    a0 = int.from_bytes(blk[:4], 'little')
    for i in range(32):
        a1, a0 = a0 ^ g(rk[i], a1), a1
    # Финальный swap и запись
    return a0.to_bytes(4,'little') + a1.to_bytes(4,'little')

def decrypt_block(blk, rk):
    """Расшифрование — ключи в обратном порядке"""
    a1 = int.from_bytes(blk[4:], 'little')
    a0 = int.from_bytes(blk[:4], 'little')
    for i in range(31, -1, -1):
        a1, a0 = a0 ^ g(rk[i], a1), a1
    return a0.to_bytes(4,'little') + a1.to_bytes(4,'little')

def pad(data):
    n = 8 - len(data) % 8
    return data + bytes([n]*n)

def unpad(data):
    return data[:-data[-1]]

def encrypt_ecb(data, key_bytes):
    rk = key_schedule(key_bytes)
    data = pad(data)
    return b''.join(encrypt_block(data[i:i+8], rk) for i in range(0,len(data),8))

def decrypt_ecb(data, key_bytes):
    rk = key_schedule(key_bytes)
    dec = b''.join(decrypt_block(data[i:i+8], rk) for i in range(0,len(data),8))
    return unpad(dec)

# ═══════════════════════ ТЕСТ ПО ГОСТ Р 34.12-2015 ═══════════════════════
def run_test():
    print("="*65)
    print("  ТЕСТ — ГОСТ Р 34.12-2015, Приложение А.2")
    print("="*65)

    KEY = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    PLAIN   = bytes.fromhex("fedcba9876543210")
    EXPECTED= "4ee901e5c2d8ca3d"

    rk = key_schedule(KEY)
    enc = encrypt_block(PLAIN, rk)
    dec = decrypt_block(enc, rk)

    print(f"\nОткрытый : {PLAIN.hex()}")
    print(f"Ожидается: {EXPECTED}")
    print(f"Получено : {enc.hex()}")
    ok = enc.hex() == EXPECTED
    print(f"Шифр     : {'✅ ВЕРНО' if ok else '❌ ОШИБКА'}")
    print(f"Расшифр  : {dec.hex()}  {'✅' if dec==PLAIN else '❌'}")

    # Тест t из А.2.1
    print(f"\n── Преобразование t (А.2.1) ──")
    for i,e in [(0xfdb97531,0x2a196f34),(0x2a196f34,0xebd9f03a),
                (0xebd9f03a,0xb039bb3d),(0xb039bb3d,0x68695433)]:
        r = t(i)
        print(f"  t({i:08x}) = {r:08x}  ожид {e:08x}  {'✅' if r==e else '❌'}")

    # Тест g из А.2.2
    print(f"\n── Преобразование g (А.2.2) ──")
    for kv,av,e in [(0x87654321,0xfedcba98,0xfdcbc20c),
                    (0xfdcbc20c,0x87654321,0x7e791a4b),
                    (0x7e791a4b,0xfdcbc20c,0xc76549ec),
                    (0xc76549ec,0x7e791a4b,0x9791c849)]:
        r = g(kv,av)
        print(f"  g[{kv:08x}]({av:08x}) = {r:08x}  ожид {e:08x}  {'✅' if r==e else '❌'}")

    # Тест >1000 символов
    print(f"\n── Тест на тексте >1000 символов ──")
    txt = (b"Magma GOST cipher test. Block=64bit Key=256bit. " * 25)  # 1175 байт
    enc2 = encrypt_ecb(txt, KEY)
    dec2 = decrypt_ecb(enc2, KEY)
    ok2  = dec2 == txt
    print(f"  Длина текста    : {len(txt)} байт")
    print(f"  Зашифровано     : {len(enc2)} байт")
    print(f"  Расшифровано    : {'✅ Совпадает' if ok2 else '❌ Не совпадает'}")
    print(f"  Шифртекст (hex) : {enc2.hex()[:64]}...")

# ═══════════════════════ МЕНЮ ═══════════════════════
def main():
    print("╔" + "═"*63 + "╗")
    print("║{:^63}║".format("МАГМА — ГОСТ Р 34.12-2015"))
    print("╚" + "═"*63 + "╝")

    while True:
        print("\nМЕНЮ:")
        print("  1. Запустить тест ГОСТ Р 34.12-2015")
        print("  2. Зашифровать текст")
        print("  3. Расшифровать (из файла)")
        print("  0. Выход")
        ch = input("\nВыбор: ").strip()

        if ch == "0":
            sys.exit(0)

        elif ch == "1":
            run_test()

        elif ch == "2":
            kh = input("Ключ (64 hex, Enter=тестовый): ").strip() or \
                 "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
            txt = input("Текст: ").encode('utf-8')
            key = bytes.fromhex(kh)
            enc = encrypt_ecb(txt, key)
            print(f"Шифртекст (hex): {enc.hex()}")
            save = input("Сохранить? (y/n): ").strip().lower()
            if save == 'y':
                fname = input("Файл (magma.bin): ").strip() or "magma.bin"
                open(fname,'wb').write(enc)
                print(f"✅ Сохранено в {fname}")

        elif ch == "3":
            fname = input("Файл: ").strip()
            kh    = input("Ключ (64 hex): ").strip()
            try:
                enc = open(fname,'rb').read()
                dec = decrypt_ecb(enc, bytes.fromhex(kh))
                print(f"Расшифровано: {dec.decode('utf-8')}")
            except Exception as e:
                print(f"❌ {e}")

if __name__ == "__main__":
    main()
