# -*- coding: utf-8 -*-
"""
Режим простой замены (ECB) для блочного шифра "Магма" (ГОСТ Р 34.12-2015)
Алфавит: строчные русские буквы (абвгдежзийклмнопрстуфхцчшщъыьэюя) – 32 символа.
Нумерация букв: а = 1, б = 2, ..., я = 32.
Перед шифрованием русского текста:
  – удаляются пробелы;
  – запятые заменяются на "зпт";
  – точки заменяются на "тчк";
  – все буквы приводятся к нижнему регистру.
Поддерживается работа с hex‑данными для контрольных примеров.
"""

import re

# ------------------------------------------------------------
# Константы русского алфавита (32 буквы, нумерация с 1)
# ------------------------------------------------------------
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ALPH_SIZE = len(ALPHABET)  # 32
LETTER_TO_NUM = {ch: i+1 for i, ch in enumerate(ALPHABET)}   # а -> 1, я -> 32
NUM_TO_LETTER = {i+1: ch for i, ch in enumerate(ALPHABET)}   # 1 -> а, 32 -> я

# ------------------------------------------------------------
# Предобработка и постобработка русского текста
# ------------------------------------------------------------
def preprocess(text: str) -> str:
    """
    Преобразует исходный текст в строку, содержащую только буквы алфавита.
    Удаляются пробелы, ',' -> "зпт", '.' -> "тчк".
    """
    result = []
    for ch in text.lower():
        if ch == ' ':
            continue
        elif ch == ',':
            result.append('зпт')
        elif ch == '.':
            result.append('тчк')
        elif ch in ALPHABET:
            result.append(ch)
        # остальные символы игнорируются
    return ''.join(result)

def postprocess(text: str) -> str:
    """Восстанавливает знаки препинания: "зпт" -> ',' , "тчк" -> '.'."""
    return text.replace('зпт', ',').replace('тчк', '.')

# ------------------------------------------------------------
# Преобразования буква <-> число (1..32) и байты
# ------------------------------------------------------------
def text_to_bytes(text: str) -> bytes:
    """Строка букв -> байты (каждое число 1..32 занимает 1 байт)."""
    nums = [LETTER_TO_NUM[ch] for ch in text]
    return bytes(nums)

def bytes_to_text(data: bytes) -> str:
    """Байты (1..32) -> строка букв."""
    nums = list(data)
    for n in nums:
        if n < 1 or n > ALPH_SIZE:
            raise ValueError(f"Некорректное значение байта {n} (допустимо 1..{ALPH_SIZE})")
    return ''.join(NUM_TO_LETTER[n] for n in nums)

# ------------------------------------------------------------
# Реализация блочного шифра "МАГМА" (ГОСТ Р 34.12-2015)
# ------------------------------------------------------------
MAGMA_SBOXES = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

def gost_round(a: int, k: int, sboxes) -> int:
    """Один раунд функции Фейстеля для Магмы (32 бита)."""
    s = (a + k) & 0xFFFFFFFF
    res = 0
    for i in range(8):
        tetrad = (s >> (4*i)) & 0xF
        new_tetrad = sboxes[i][tetrad]
        res |= (new_tetrad << (4*i))
    # циклический сдвиг влево на 11 бит
    res = ((res << 11) | (res >> (32 - 11))) & 0xFFFFFFFF
    return res

def gost_key_schedule(key_bytes: bytes):
    """
    Расширение ключа для Магмы.
    key_bytes – 32 байта.
    Возвращает список из 32 раундовых 32‑битных ключей.
    """
    if len(key_bytes) != 32:
        raise ValueError("Ключ должен быть ровно 32 байта")
    K = []
    for i in range(8):
        b = key_bytes[4*i:4*i+4]
        val = (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]
        K.append(val)
    # Для Магмы порядок: K0..K7, затем повтор 3 раза, затем обратный порядок
    round_keys = K * 3 + K[::-1]
    return round_keys

def magma_encrypt_block(block: int, round_keys) -> int:
    """
    Шифрование одного 64‑битного блока алгоритмом Магма.
    """
    a1 = (block >> 32) & 0xFFFFFFFF
    a0 = block & 0xFFFFFFFF
    for i in range(31):
        a1, a0 = a0, a1 ^ gost_round(a0, round_keys[i], MAGMA_SBOXES)
    # последний раунд без перестановки
    a1 = a1 ^ gost_round(a0, round_keys[31], MAGMA_SBOXES)
    return (a1 << 32) | a0

def magma_decrypt_block(block: int, round_keys) -> int:
    """
    Расшифрование одного 64‑битного блока алгоритмом Магма.
    """
    a1 = (block >> 32) & 0xFFFFFFFF
    a0 = block & 0xFFFFFFFF
    # первый шаг — обратный последнему раунду
    a1 = a1 ^ gost_round(a0, round_keys[31], MAGMA_SBOXES)
    for i in range(30, -1, -1):
        new_a1 = a0 ^ gost_round(a1, round_keys[i], MAGMA_SBOXES)
        new_a0 = a1
        a1, a0 = new_a1, new_a0
    return (a1 << 32) | a0

# ------------------------------------------------------------
# Режим простой замены (ECB) по ГОСТ Р 34.13-2015
# ------------------------------------------------------------
def ecb_encrypt(data: bytes, key_bytes: bytes) -> bytes:
    """
    Шифрование данных в режиме простой замены (ECB).
    data – входные байты, длина должна быть кратна 8.
    key_bytes – 32 байта ключа.
    Возвращает зашифрованные байты.
    """
    if len(key_bytes) != 32:
        raise ValueError("Ключ должен быть 32 байта")
    if len(data) % 8 != 0:
        # Для контрольных примеров длина всегда кратна 8, но на всякий случай дополним нулями
        # В реальности нужно применять процедуру дополнения, но здесь просто для удобства
        data = data + b'\x00' * (8 - len(data) % 8)
    round_keys = gost_key_schedule(key_bytes)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = int.from_bytes(data[i:i+8], 'big')
        enc_block = magma_encrypt_block(block, round_keys)
        result.extend(enc_block.to_bytes(8, 'big'))
    return bytes(result)

def ecb_decrypt(data: bytes, key_bytes: bytes) -> bytes:
    """
    Расшифрование данных в режиме простой замены (ECB).
    data – входные байты, длина должна быть кратна 8.
    key_bytes – 32 байта ключа.
    Возвращает расшифрованные байты.
    """
    if len(key_bytes) != 32:
        raise ValueError("Ключ должен быть 32 байта")
    if len(data) % 8 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 8")
    round_keys = gost_key_schedule(key_bytes)
    result = bytearray()
    for i in range(0, len(data), 8):
        block = int.from_bytes(data[i:i+8], 'big')
        dec_block = magma_decrypt_block(block, round_keys)
        result.extend(dec_block.to_bytes(8, 'big'))
    return bytes(result)

# ------------------------------------------------------------
# Функции для работы с русским текстом в ECB
# ------------------------------------------------------------
def encrypt_russian_ecb(plain_text: str, key_hex: str) -> str:
    """Шифрование русского текста в ECB, возвращает шифртекст в hex."""
    processed = preprocess(plain_text)
    if not processed:
        return ""
    data = text_to_bytes(processed)
    # Дополняем до кратности 8 нулями (для русского текста)
    pad_len = (8 - len(data) % 8) % 8
    data += b'\x00' * pad_len
    key = bytes.fromhex(key_hex)
    cipher = ecb_encrypt(data, key)
    return cipher.hex().upper()

def decrypt_russian_ecb(cipher_hex: str, key_hex: str) -> str:
    """Расшифрование русского текста в ECB, возвращает восстановленный текст (после предобработки)."""
    key = bytes.fromhex(key_hex)
    cipher = bytes.fromhex(cipher_hex)
    plain = ecb_decrypt(cipher, key)
    # Удаляем нулевые байты в конце (дополнение)
    plain = plain.rstrip(b'\x00')
    return bytes_to_text(plain)

# ------------------------------------------------------------
# Вспомогательная функция для ввода hex с проверкой
# ------------------------------------------------------------
def input_hex(prompt: str, required_length: int = None) -> str:
    """
    Ввод hex-строки, удаление пробелов, опциональная проверка длины.
    Возвращает очищенную строку без пробелов и префикса 0x.
    """
    s = input(prompt).strip().replace(' ', '')
    if s.startswith('0x') or s.startswith('0X'):
        s = s[2:]
    if required_length is not None and len(s) != required_length:
        raise ValueError(f"Должно быть ровно {required_length} hex-символов")
    return s

# ------------------------------------------------------------
# Главное меню
# ------------------------------------------------------------
def main():
    print("="*50)
    print("   ПРОСТАЯ ЗАМЕНА (ECB) ПО ГОСТ Р 34.13-2015")
    print("   Блочный шифр МАГМА (ГОСТ Р 34.12-2015)")
    print("="*50)
    while True:
        print("\nМеню:")
        print("1. Шифрование (русский текст)")
        print("2. Расшифрование (русский текст)")
        print("3. Шифрование (hex данные / контрольные примеры)")
        print("4. Расшифрование (hex данные)")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == '0':
            print("Работа завершена.")
            break

        # Ввод ключа (общий для всех режимов)
        print("\n--- Параметры ключа ---")
        try:
            key_hex = input_hex("Введите ключ (64 hex символа): ", 64)
        except ValueError as e:
            print("Ошибка:", e)
            continue

        if choice == '1':
            # Шифрование русского текста
            text = input("Введите открытый текст (русский): ")
            try:
                cipher_hex = encrypt_russian_ecb(text, key_hex)
                if cipher_hex:
                    print("\n--- Результат шифрования ---")
                    print("Шифртекст (hex):", cipher_hex)
                else:
                    print("Текст пуст после предобработки.")
            except Exception as e:
                print("Ошибка:", e)

        elif choice == '2':
            # Расшифрование русского текста
            cipher_hex = input_hex("Введите шифртекст (hex): ").upper()
            try:
                plain_processed = decrypt_russian_ecb(cipher_hex, key_hex)
                print("\n--- Результат расшифрования ---")
                print("Расшифрованный текст (после предобработки):", plain_processed)
                resp = input("Выполнить обратную замену 'зпт'→',' и 'тчк'→'.'? (y/n): ").strip().lower()
                if resp == 'y':
                    restored = postprocess(plain_processed)
                    print("Текст после обратной замены:", restored)
            except Exception as e:
                print("Ошибка:", e)

        elif choice == '3':
            # Шифрование hex-данных
            plain_hex = input_hex("Введите открытый текст (hex, произвольная длина): ").upper()
            try:
                plain_bytes = bytes.fromhex(plain_hex)
                key_bytes = bytes.fromhex(key_hex)
                # В ECB длина должна быть кратна 8, дополним при необходимости
                if len(plain_bytes) % 8 != 0:
                    print("Длина входных данных не кратна 8, будет выполнено дополнение нулями.")
                    plain_bytes += b'\x00' * (8 - len(plain_bytes) % 8)
                cipher_bytes = ecb_encrypt(plain_bytes, key_bytes)
                print("\n--- Результат шифрования ---")
                print("Шифртекст (hex):", cipher_bytes.hex().upper())
            except Exception as e:
                print("Ошибка:", e)

        elif choice == '4':
            # Расшифрование hex-данных
            cipher_hex = input_hex("Введите шифртекст (hex): ").upper()
            try:
                cipher_bytes = bytes.fromhex(cipher_hex)
                key_bytes = bytes.fromhex(key_hex)
                if len(cipher_bytes) % 8 != 0:
                    raise ValueError("Длина шифртекста должна быть кратна 8")
                plain_bytes = ecb_decrypt(cipher_bytes, key_bytes)
                print("\n--- Результат расшифрования ---")
                print("Открытый текст (hex):", plain_bytes.hex().upper())
            except Exception as e:
                print("Ошибка:", e)

        else:
            print("Неверный выбор. Повторите.")

if __name__ == "__main__":
    main()