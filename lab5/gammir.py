import sys
import struct

# =====================================================================
# МАГМА (ГОСТ Р 34.12-2015) — блок 64 бит, ключ 256 бит
# Режим гаммирования CTR (ГОСТ Р 34.13-2015)
# =====================================================================

# S-блоки π0'..π7' из раздела 5.1.1 ГОСТ Р 34.12-2015
PI = [
    [12, 4,  6,  2, 10,  5, 11,  9, 14,  8, 13,  7,  0,  3, 15,  1],  # π0
    [ 6,  8,  2,  3,  9, 10,  5, 12,  1, 14,  4,  7, 11, 13,  0, 15],  # π1
    [11,  3,  5,  8,  2, 15, 10, 13, 14,  1,  7,  4, 12,  9,  6,  0],  # π2
    [12,  8,  2,  1, 13,  4, 15,  6,  7,  0, 10,  5,  3, 14,  9, 11],  # π3
    [ 7, 15,  5, 10,  8,  1,  6, 13,  0,  9,  3, 14, 11,  4,  2, 12],  # π4
    [ 5, 13, 15,  6,  9,  2, 12, 10, 11,  7,  8,  1,  4,  3, 14,  0],  # π5
    [ 8, 14,  2,  5,  6,  9,  1, 12, 15,  4, 11,  0, 13, 10,  3,  7],  # π6
    [ 1,  7, 14, 13,  0,  5,  8,  3,  4, 15, 10,  6,  9, 12, 11,  2],  # π7
]


def t_transform(x: int) -> int:
    """t: V32 → V32 — нелинейная подстановка через S-блоки (формула 14)"""
    result = 0
    for i in range(8):          # i=0 → младший ниббл → π0
        nibble = (x >> (4 * i)) & 0xF
        result |= PI[i][nibble] << (4 * i)
    return result


def left_shift_11(x: int) -> int:
    """Циклический сдвиг 32-битного слова влево на 11 бит (⋘11)"""
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF


def g(k: int, a: int) -> int:
    """g[k](a) = (t(a ⊞ k)) ⋘11   (формула 15 ГОСТ Р 34.12-2015)"""
    return left_shift_11(t_transform((a + k) & 0xFFFFFFFF))


# ─────────────────────────────────────────────────────────────────────
# Развертывание ключа — раздел 5.3 ГОСТ Р 34.12-2015
# ─────────────────────────────────────────────────────────────────────

def key_schedule(key_bytes: bytes) -> list:
    """
    256-битный ключ → 32 итерационных подключа.
    Раунды  1-24: K1, K2, ..., K8  (три раза)
    Раунды 25-32: K8, K7, ..., K1  (обратный порядок)
    """
    K = list(struct.unpack('>8I', key_bytes))   # K1..K8 (big-endian)
    return K * 3 + K[::-1]                       # всего 32 ключа


# ─────────────────────────────────────────────────────────────────────
# Базовый блочный шифр МАГМА — раздел 5.4
# ─────────────────────────────────────────────────────────────────────

def magma_encrypt_block(block: bytes, round_keys: list) -> bytes:
    """
    Зашифрование одного 64-битного блока:
    E(a) = G*[K32] G[K31] ... G[K1] (a1, a0)
    G[k](a1,a0) = (a0, g[k](a0) ⊕ a1)   — раунды 1..31
    G*[k](a1,a0) = (g[k](a0) ⊕ a1) || a0 — последний раунд без свопа
    """
    a1, a0 = struct.unpack('>II', block)   # a = a1||a0

    for i in range(31):                    # раунды 1..31
        a1, a0 = a0, g(round_keys[i], a0) ^ a1

    a1 = g(round_keys[31], a0) ^ a1       # раунд 32 (G* — без свопа)
    return struct.pack('>II', a1, a0)


def magma_decrypt_block(block: bytes, round_keys: list) -> bytes:
    """Расшифрование = зашифрование с ключами в обратном порядке (формула 20)"""
    return magma_encrypt_block(block, round_keys[::-1])


# ─────────────────────────────────────────────────────────────────────
# Режим гаммирования CTR — ГОСТ Р 34.13-2015
# ci = mi ⊕ E_K(CTRi),  CTRi = (CTR0 + i) mod 2^64
# ─────────────────────────────────────────────────────────────────────

def ctr_process(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Гаммирование CTR — шифрование и расшифрование идентичны.
    data : открытый или шифрованный текст (байты)
    key  : 32 байта (256 бит)
    iv   : синхропосылка 4 байт (64 бит) = начальное значение счётчика
    """
    rk  = key_schedule(key)
    ctr = int.from_bytes(iv, 'big')
    out = bytearray()

    for i in range(0, len(data), 8):
        gamma = magma_encrypt_block(ctr.to_bytes(8, 'big'), rk)
        chunk = data[i:i + 8]
        out.extend(b ^ gm for b, gm in zip(chunk, gamma))
        ctr = (ctr + 1) & 0xFFFFFFFFFFFFFFFF  # +1 mod 2^64

    return bytes(out)


# ─────────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ─────────────────────────────────────────────────────────────────────

def input_hex(prompt: str, byte_len: int) -> bytes:
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) == byte_len * 2:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print(f"  [!] Нужно ровно {byte_len * 2} HEX-символов ({byte_len} байт)")


def input_hex_any(prompt: str) -> bytes:
    while True:
        raw = input(prompt).strip().replace(' ', '')
        if len(raw) % 2 == 0 and len(raw) > 0:
            try:
                return bytes.fromhex(raw)
            except ValueError:
                pass
        print("  [!] Введите корректную HEX-строку чётной длины")


def print_hex(label: str, data: bytes, bsize: int = 8):
    blocks = ' '.join(data[i:i + bsize].hex().upper()
                      for i in range(0, len(data), bsize))
    print(f"  {label}: {blocks}")


# ─────────────────────────────────────────────────────────────────────
# Контрольный пример (Приложение А.2 ГОСТ Р 34.12-2015)
# Ключ и данные: таблица из стандарта
# ─────────────────────────────────────────────────────────────────────

def run_self_test():
    print("\n" + "=" * 62)
    print("  Контрольный пример  ГОСТ Р 34.12-2015 (Приложение А.2)")
    print("=" * 62)

    # Ключ из А.2.3
    key_hex = ("ffeeddccbbaa9988"
               "7766554433221100"
               "f0f1f2f3f4f5f6f7"
               "f8f9fafbfcfdfeff")
    pt_hex       = "fedcba9876543210"
    ct_expected  = "4ee901e5c2d8ca3d"

    key = bytes.fromhex(key_hex)
    pt  = bytes.fromhex(pt_hex)
    rk  = key_schedule(key)
    ct  = magma_encrypt_block(pt, rk)
    dec = magma_decrypt_block(ct, rk)

    print(f"  Ключ          : {key.hex()}")
    print(f"  Открытый текст: {pt_hex}")
    print(f"  Ожидается     : {ct_expected}")
    print(f"  Получено      : {ct.hex()}")
    print(f"  Шифр          : {'✓  ПРОЙДЕН' if ct.hex() == ct_expected else '✗  ОШИБКА'}")
    print(f"  Расшифровано  : {dec.hex()}")
    print(f"  Расшифровка   : {'✓  ВЕРНО'   if dec == pt else '✗  ОШИБКА'}")

    # ── Демонстрация CTR-режима ──────────────────────────────────────
    print()
    print("  --- Демонстрация CTR-режима ---")
    iv      = bytes.fromhex("1234567890abcdef")
    message = bytes.fromhex("fedcba9876543210" * 2)   # 16 байт

    encrypted = ctr_process(message, key, iv)
    decrypted = ctr_process(encrypted, key, iv)

    print_hex("  Открытый текст", message)
    print_hex("  Гамма (CTR)   ", encrypted)
    print_hex("  Расшифровано  ", decrypted)
    print(f"  Расшифровка CTR: {'✓  ВЕРНО' if decrypted == message else '✗  ОШИБКА'}")
    print()


# ─────────────────────────────────────────────────────────────────────
# Меню гаммирования
# ─────────────────────────────────────────────────────────────────────

def gamma_menu():
    print("\n--- Гаммирование CTR (ГОСТ Р 34.13-2015 / МАГМА) ---\n")

    key = input_hex("Ключ           (32 байта, 64 HEX-символа) : ", 32)
    iv  = input_hex("Синхропосылка  ( 8 байт,  16 HEX-символов): ",  8)

    print("\n  1. Зашифровать")
    print("  2. Расшифровать")
    op = input("  Действие: ").strip()

    if op not in ("1", "2"):
        print("  [!] Неверный выбор")
        return

    data   = input_hex_any("Данные (HEX): ")
    result = ctr_process(data, key, iv)

    print()
    if op == "1":
        print_hex("Открытый текст", data)
        print_hex("Шифртекст     ", result)
    else:
        print_hex("Шифртекст     ", data)
        print_hex("Открытый текст", result)


# ─────────────────────────────────────────────────────────────────────
# Главный цикл
# ─────────────────────────────────────────────────────────────────────

while True:
    print("""
╔══════════════════════════════════════════════════════════╗
║   Гаммирование  ГОСТ Р 34.13-2015  (МАГМА)              ║
╠══════════════════════════════════════════════════════════╣
║  1. Зашифровать / Расшифровать (CTR)                     ║
║  2. Контрольный пример (ГОСТ Р 34.12-2015, прил. А.2)   ║
║  3. Выход                                                ║
╚══════════════════════════════════════════════════════════╝""")

    choice = input("Выбор: ").strip()

    if choice == "3":
        sys.exit()
    elif choice == "1":
        gamma_menu()
    elif choice == "2":
        run_self_test()
    else:
        print("  [!] Неверный выбор!")
