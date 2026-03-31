#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   ГОСТ Р 34.12-2015 — Блочный шифр «Магма»                  ║
║   Длина блока: 64 бит | Ключ: 256 бит                        ║
║   Структура:   32-раундовая сеть Фейстеля                    ║
║   Контрольный пример (Приложение А.2):                       ║
║     Ключ: ffeeddcc...fcfdfeff                                ║
║     Открытый текст: fedcba9876543210                         ║
║     Шифртекст:      4ee901e5c2d8ca3d                         ║
╚══════════════════════════════════════════════════════════════╝
"""
import os, sys

# ══════════════════════════════════════════════════════════════
#   S-БЛОКИ (раздел 5.1.1 ГОСТ Р 34.12-2015)
# ══════════════════════════════════════════════════════════════
PI = [
    [12,  4,  6,  2, 10,  5, 11,  9, 14,  8, 13,  7,  0,  3, 15,  1],
    [ 6,  8,  2,  3,  9, 10,  5, 12,  1, 14,  4,  7, 11, 13,  0, 15],
    [11,  3,  5,  8,  2, 15, 10, 13, 14,  1,  7,  4, 12,  9,  6,  0],
    [12,  8,  2,  1, 13,  4, 15,  6,  7,  0, 10,  5,  3, 14,  9, 11],
    [ 7, 15,  5, 10,  8,  1,  6, 13,  0,  9,  3, 14, 11,  4,  2, 12],
    [ 5, 13, 15,  6,  9,  2, 12, 10, 11,  7,  8,  1,  4,  3, 14,  0],
    [ 8, 14,  2,  5,  6,  9,  1, 12, 15,  4, 11,  0, 13, 10,  3,  7],
    [ 1,  7, 14, 13,  0,  5,  8,  3,  4, 15, 10,  6,  9, 12, 11,  2],
]

# ══════════════════════════════════════════════════════════════
#   ЯДРО АЛГОРИТМА
# ══════════════════════════════════════════════════════════════
def t_transform(a: int) -> int:
    """Формула 14: нелинейная подстановка через 8 S-блоков по 4 бита."""
    r = 0
    for i in range(8):
        r |= PI[i][(a >> (4 * i)) & 0xF] << (4 * i)
    return r

def g_transform(k: int, a: int) -> int:
    """Формула 15: g[k](a) = (t(a ⊞ k)) ⋘ 11"""
    s = (a + k) & 0xFFFF_FFFF
    s = t_transform(s)
    return ((s << 11) | (s >> 21)) & 0xFFFF_FFFF

def G_round(k: int, a1: int, a0: int) -> tuple:
    """Формула 16: раунд Фейстеля СО свопом (раунды 1–31)."""
    return a0, g_transform(k, a0) ^ a1

def G_last(k: int, a1: int, a0: int) -> tuple:
    """Формула 17: финальный раунд БЕЗ свопа (раунд 32 / раунд 1)."""
    return g_transform(k, a0) ^ a1, a0

def key_schedule(key: bytes) -> list:
    """Формула 18: K1..K8 × 3, затем K8..K1 = 32 итерационных ключа."""
    K = [int.from_bytes(key[i * 4:(i + 1) * 4], 'big') for i in range(8)]
    return K * 3 + K[::-1]

def encrypt_block(block: bytes, key: bytes) -> bytes:
    """Формула 19: зашифрование одного 64-битного блока."""
    rk = key_schedule(key)
    a  = int.from_bytes(block, 'big')
    a1, a0 = (a >> 32) & 0xFFFF_FFFF, a & 0xFFFF_FFFF
    for i in range(31):
        a1, a0 = G_round(rk[i], a1, a0)
    a1, a0 = G_last(rk[31], a1, a0)
    return ((a1 << 32) | a0).to_bytes(8, 'big')

def decrypt_block(block: bytes, key: bytes) -> bytes:
    """Формула 20: расшифрование одного 64-битного блока."""
    rk = key_schedule(key)
    b  = int.from_bytes(block, 'big')
    b1, b0 = (b >> 32) & 0xFFFF_FFFF, b & 0xFFFF_FFFF
    for i in range(31, 0, -1):
        b1, b0 = G_round(rk[i], b1, b0)
    b1, b0 = G_last(rk[0], b1, b0)
    return ((b1 << 32) | b0).to_bytes(8, 'big')

# ══════════════════════════════════════════════════════════════
#   PKCS7 PADDING — только для текстового режима
# ══════════════════════════════════════════════════════════════
def pad(data: bytes) -> bytes:
    n = 8 - (len(data) % 8)
    return data + bytes([n] * n)

def unpad(data: bytes) -> bytes:
    n = data[-1]
    if n < 1 or n > 8:
        raise ValueError("Неверный padding — возможно неправильный ключ или режим.")
    return data[:-n]

# ══════════════════════════════════════════════════════════════
#   ECB-РЕЖИМ
#   use_padding=True  → текст (произвольная длина)
#   use_padding=False → hex  (данные кратны 8 байтам)
# ══════════════════════════════════════════════════════════════
def encrypt_ecb(pt: bytes, key: bytes, use_padding: bool) -> bytes:
    data = pad(pt) if use_padding else pt
    result = b""
    for i in range(0, len(data), 8):
        result += encrypt_block(data[i:i + 8], key)
    return result

def decrypt_ecb(ct: bytes, key: bytes, use_padding: bool) -> bytes:
    result = b""
    for i in range(0, len(ct), 8):
        result += decrypt_block(ct[i:i + 8], key)
    return unpad(result) if use_padding else result

# ══════════════════════════════════════════════════════════════
#   ФАЙЛ РЕЗУЛЬТАТОВ
# ══════════════════════════════════════════════════════════════
RESULT_FILE = "magma_results.txt"
SEP1 = "═" * 62
SEP2 = "─" * 62

def save_result(content: str):
    with open(RESULT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def init_file():
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write("ГОСТ Р 34.12-2015 — «Магма» | Журнал операций\n")
        f.write(SEP1 + "\n")

# ══════════════════════════════════════════════════════════════
#   ФУНКЦИИ ВВОДА
# ══════════════════════════════════════════════════════════════
def input_key() -> bytes:
    print(f"  {SEP2}")
    print("  Ключ — 64 hex-символа (256 бит).")
    print("  Пример: ffeeddccbbaa99887766554433221100"
          "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff")
    while True:
        raw = input("  Ключ: ").strip().replace(" ", "")
        if len(raw) == 64:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print(f"  ⚠  Введено {len(raw)} символов — нужно ровно 64.\n")

def input_plaintext() -> tuple:
    print(f"  {SEP2}")
    print("  [1] Текст (UTF-8) — например: Привет Мир!")
    print("  [2] Hex-строка    — например: fedcba9876543210")
    while True:
        c = input("  Выбор [1/2]: ").strip()
        if c == "1":
            t = input("  Открытый текст: ")
            return t.encode("utf-8"), "text"
        elif c == "2":
            raw = input("  Hex: ").strip().replace(" ", "")
            if len(raw) % 16 != 0:
                print(f"  ⚠  Длина {len(raw)} — нужна кратность 16.\n")
                continue
            try:
                return bytes.fromhex(raw), "hex"
            except ValueError:
                print("  ⚠  Некорректные hex-символы.\n")
        else:
            print("  ⚠  Введите 1 или 2.\n")

def input_ciphertext() -> bytes:
    print(f"  {SEP2}")
    print("  Шифртекст в hex (кратно 16 символам).")
    print("  Пример: 4ee901e5c2d8ca3d")
    while True:
        raw = input("  Шифртекст: ").strip().replace(" ", "")
        if len(raw) % 16 != 0:
            print(f"  ⚠  Длина {len(raw)} — нужна кратность 16.\n")
            continue
        try:
            return bytes.fromhex(raw)
        except ValueError:
            print("  ⚠  Некорректные hex-символы.\n")

def input_decrypt_mode() -> bool:
    print(f"  {SEP2}")
    print("  Как был зашифрован текст?")
    print("  [1] Из текста (UTF-8) — с padding")
    print("  [2] Из hex-строки     — без padding")
    while True:
        c = input("  Выбор [1/2]: ").strip()
        if c == "1": return True
        if c == "2": return False
        print("  ⚠  Введите 1 или 2.\n")

# ══════════════════════════════════════════════════════════════
#   МЕНЮ: ШИФРОВАНИЕ
# ══════════════════════════════════════════════════════════════
def menu_encrypt():
    print(f"\n{SEP1}\n  🔒  ЗАШИФРОВАНИЕ\n{SEP1}")
    key      = input_key()
    pt, mode = input_plaintext()
    use_pad  = (mode == "text")       # hex → без padding, текст → с padding
    ct       = encrypt_ecb(pt, key, use_padding=use_pad)
    pt_show  = pt.decode("utf-8", errors="replace") if mode == "text" else pt.hex()

    print(f"\n{SEP1}")
    print("  РЕЗУЛЬТАТ:")
    print(SEP2)
    print(f"  Ключ           : {key.hex()}")
    print(f"  Открытый текст : {pt_show}")
    print(f"  Hex            : {pt.hex()}")
    print(f"  Шифртекст      : {ct.hex()}")
    print(SEP1)

    save_result(
        f"\n{SEP1}\n"
        f"  ОПЕРАЦИЯ   : ЗАШИФРОВАНИЕ\n"
        f"  АЛГОРИТМ   : ГОСТ Р 34.12-2015 «Магма» (ECB, 64-бит)\n"
        f"{SEP2}\n"
        f"  КЛЮЧ       : {key.hex()}\n"
        f"  ОТКРЫТЫЙ   : {pt_show}\n"
        f"  HEX        : {pt.hex()}\n"
        f"  ШИФРТЕКСТ  : {ct.hex()}\n"
        f"{SEP1}"
    )
    print(f"\n  ✅ Сохранено → {RESULT_FILE}\n")

# ══════════════════════════════════════════════════════════════
#   МЕНЮ: РАСШИФРОВАНИЕ
# ══════════════════════════════════════════════════════════════
def menu_decrypt():
    print(f"\n{SEP1}\n  🔓  РАСШИФРОВАНИЕ\n{SEP1}")
    use_pad = input_decrypt_mode()
    key     = input_key()
    ct      = input_ciphertext()

    try:
        pt   = decrypt_ecb(ct, key, use_padding=use_pad)
        text = pt.decode("utf-8", errors="replace")

        print(f"\n{SEP1}")
        print("  РЕЗУЛЬТАТ:")
        print(SEP2)
        print(f"  Ключ           : {key.hex()}")
        print(f"  Шифртекст      : {ct.hex()}")
        print(f"  Открытый текст : {text}")
        print(f"  Hex            : {pt.hex()}")
        print(SEP1)

        save_result(
            f"\n{SEP1}\n"
            f"  ОПЕРАЦИЯ   : РАСШИФРОВАНИЕ\n"
            f"  АЛГОРИТМ   : ГОСТ Р 34.12-2015 «Магма» (ECB, 64-бит)\n"
            f"{SEP2}\n"
            f"  КЛЮЧ       : {key.hex()}\n"
            f"  ШИФРТЕКСТ  : {ct.hex()}\n"
            f"  ОТКРЫТЫЙ   : {text}\n"
            f"  HEX        : {pt.hex()}\n"
            f"{SEP1}"
        )
        print(f"\n  ✅ Сохранено → {RESULT_FILE}\n")

    except Exception as e:
        print(f"\n  ❌ Ошибка: {e}\n")

# ══════════════════════════════════════════════════════════════
#   МЕНЮ: ПРОСМОТР ФАЙЛА
# ══════════════════════════════════════════════════════════════
def menu_show_file():
    print(f"\n{SEP1}\n  📄  {RESULT_FILE}\n{SEP1}")
    if not os.path.exists(RESULT_FILE):
        print("  Файл пуст.\n")
        return
    with open(RESULT_FILE, encoding="utf-8") as f:
        print(f.read())

# ══════════════════════════════════════════════════════════════
#   АВТОТЕСТ:  python magma.py test
# ══════════════════════════════════════════════════════════════
def run_tests():
    KEY = bytes.fromhex(
        "ffeeddccbbaa99887766554433221100"
        "f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    )
    print(SEP1)
    print("  АВТОТЕСТ — контрольные примеры ГОСТ Р 34.12-2015 А.2")
    print(SEP1)
    cases = [
        ("t(fdb97531)",            f"{t_transform(0xfdb97531):08x}", "2a196f34"),
        ("t(2a196f34)",            f"{t_transform(0x2a196f34):08x}", "ebd9f03a"),
        ("t(ebd9f03a)",            f"{t_transform(0xebd9f03a):08x}", "b039bb3d"),
        ("t(b039bb3d)",            f"{t_transform(0xb039bb3d):08x}", "68695433"),
        ("g[87654321](fedcba98)",  f"{g_transform(0x87654321,0xfedcba98):08x}", "fdcbc20c"),
        ("g[fdcbc20c](87654321)",  f"{g_transform(0xfdcbc20c,0x87654321):08x}", "7e791a4b"),
    ]
    print()
    for label, got, exp in cases:
        print(f"  {'✅' if got==exp else '❌'} {label:<32} = {got}  (ожид: {exp})")
    PT = bytes.fromhex("fedcba9876543210")
    ct = encrypt_ecb(PT, KEY, use_padding=False)
    pt_back = decrypt_ecb(ct, KEY, use_padding=False)
    print(f"\n  {'✅' if ct.hex()=='4ee901e5c2d8ca3d' else '❌'} Шифрование:    {PT.hex()} → {ct.hex()}")
    print(f"  {'✅' if pt_back==PT else '❌'} Расшифрование: {ct.hex()} → {pt_back.hex()}")
    TEXT = "ГОСТ Магма тест"
    ct2 = encrypt_ecb(TEXT.encode("utf-8"), KEY, use_padding=True)
    pt2 = decrypt_ecb(ct2, KEY, use_padding=True).decode("utf-8")
    print(f"  {'✅' if pt2==TEXT else '❌'} Текст: '{TEXT}' → '{pt2}'")
    print(f"\n{SEP1}\n  Все тесты пройдены!\n{SEP1}")

# ══════════════════════════════════════════════════════════════
#   ГЛАВНОЕ МЕНЮ
# ══════════════════════════════════════════════════════════════
def main():
    init_file()
    while True:
        print(f"\n{SEP1}")
        print("  ГОСТ Р 34.12-2015 — Блочный шифр «Магма»")
        print("  Сеть Фейстеля | 64-бит блок | 256-бит ключ")
        print(SEP1)
        print("  [1]  🔒  Зашифровать")
        print("  [2]  🔓  Расшифровать")
        print("  [3]  📄  Показать файл результатов")
        print("  [0]  ❌  Выход")
        print(SEP2)
        c = input("  Выбор: ").strip()
        if   c == "1": menu_encrypt()
        elif c == "2": menu_decrypt()
        elif c == "3": menu_show_file()
        elif c == "0": print("\n  До свидания!\n"); break
        else:          print("  ⚠  Введите 0, 1, 2 или 3.\n")

# ══════════════════════════════════════════════════════════════
#   ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_tests()
    else:
        main()
