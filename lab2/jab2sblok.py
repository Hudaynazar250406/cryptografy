import sys
import struct

# =============================================================================
# Общие данные и функции для всех шифров (русский алфавит из 32 букв)
# =============================================================================
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
N = len(ALPHABET)

def preprocess_open_text(text: str) -> str:
    """
    Подготовка открытого текста перед шифрованием:
    1. Приведение к нижнему регистру.
    2. Замена ',' -> 'зпт', '.' -> 'тчк'.
    3. Удаление всех символов, не входящих в алфавит (включая пробелы).
    Возвращает строку только из букв алфавита.
    """
    text = text.lower()
    text = text.replace(',', 'зпт')
    text = text.replace('.', 'тчк')
    # Оставляем только буквы алфавита
    result = ''.join(ch for ch in text if ch in ALPHABET)
    return result

def postprocess_decrypted(text: str) -> str:
    """
    Восстановление знаков препинания в расшифрованном тексте:
    Замена 'зпт' -> ',', 'тчк' -> '.'.
    """
    text = text.replace('тчк', '.')
    text = text.replace('зпт', ',')
    return text

def filter_alphabet(text: str) -> str:
    """Оставляет в строке только символы алфавита (для расшифрования)."""
    return ''.join(ch for ch in text.lower() if ch in ALPHABET)

# =============================================================================
# 1. Шифр Тритемия
# =============================================================================
def trithemius_encrypt(plain: str) -> str:
    cipher = []
    for i, ch in enumerate(plain):
        p = ALPHABET.index(ch)
        shift = i % N
        c = (p + shift) % N
        cipher.append(ALPHABET[c])
    return ''.join(cipher)

def trithemius_decrypt(cipher: str) -> str:
    plain = []
    for i, ch in enumerate(cipher):
        c = ALPHABET.index(ch)
        shift = i % N
        p = (c - shift) % N
        plain.append(ALPHABET[p])
    return ''.join(plain)

def trithemius_main():
    print("\n=== Шифр Тритемия ===")
    print("Алфавит (32 буквы):", ALPHABET)
    print()
    print("Выберите режим:")
    print("1 - шифрование открытого текста")
    print("2 - расшифрование криптотекста")
    choice = input("Ваш выбор (1/2): ").strip()

    if choice == '1':
        print("\n--- ШИФРОВАНИЕ ---")
        raw = input("Введите открытый текст: ")
        processed = preprocess_open_text(raw)
        print("Обработанный текст (только буквы, знаки -> зпт/тчк):", processed)
        if not processed:
            print("Ошибка: после обработки не осталось букв для шифрования.")
            return
        encrypted = trithemius_encrypt(processed)
        print("Зашифрованный текст:", encrypted)

    elif choice == '2':
        print("\n--- РАСШИФРОВАНИЕ ---")
        raw = input("Введите криптотекст: ")
        filtered = filter_alphabet(raw)
        print("Отфильтрованный криптотекст (только буквы):", filtered)
        if not filtered:
            print("Ошибка: криптотекст не содержит допустимых символов.")
            return
        decrypted = trithemius_decrypt(filtered)
        print("Расшифрованный текст (буквы):", decrypted)
        restored = postprocess_decrypted(decrypted)
        print("Текст после замены зпт/тчк на знаки препинания:", restored)

    else:
        print("Неверный выбор. Возврат в главное меню.")

# =============================================================================
# 2. Шифр Белазо (Виженер с ключевым словом)
# =============================================================================
def validate_key(key: str) -> bool:
    return all(ch in ALPHABET for ch in key.lower())

def input_key() -> str:
    while True:
        key = input("Введите ключ (только буквы алфавита): ").strip().lower()
        if not key:
            print("Ключ не может быть пустым. Повторите ввод.")
            continue
        if not validate_key(key):
            print("Ошибка: ключ может содержать только буквы алфавита!")
            print("Допустимые символы:", ALPHABET)
            continue
        if len(set(key)) == 1:
            print("Ошибка: все символы ключа не могут быть одинаковыми. Введите ключ с разными символами.")
            continue
        return key

def belazo_encrypt(plain: str, key: str) -> str:
    key_vals = [ALPHABET.index(ch) for ch in key]
    key_len = len(key_vals)
    cipher = []
    for i, ch in enumerate(plain):
        p = ALPHABET.index(ch)
        k = key_vals[i % key_len]
        c = (p + k) % N
        cipher.append(ALPHABET[c])
    return ''.join(cipher)

def belazo_decrypt(cipher: str, key: str) -> str:
    key_vals = [ALPHABET.index(ch) for ch in key]
    key_len = len(key_vals)
    plain = []
    for i, ch in enumerate(cipher):
        c = ALPHABET.index(ch)
        k = key_vals[i % key_len]
        p = (c - k) % N
        plain.append(ALPHABET[p])
    return ''.join(plain)

def belazo_main():
    print("\n=== Шифр Белазо (Виженер) ===")
    print("Алфавит (32 буквы):", ALPHABET)
    print()
    print("Выберите режим:")
    print("1 - шифрование открытого текста")
    print("2 - расшифрование криптотекста")
    choice = input("Ваш выбор (1/2): ").strip()

    if choice == '1':
        print("\n--- ШИФРОВАНИЕ ---")
        raw = input("Введите открытый текст: ")
        processed = preprocess_open_text(raw)
        print("Обработанный текст (только буквы, знаки -> зпт/тчк):", processed)
        if not processed:
            print("Ошибка: после обработки не осталось букв для шифрования.")
            return
        key = input_key()
        encrypted = belazo_encrypt(processed, key)
        print("Зашифрованный текст:", encrypted)

    elif choice == '2':
        print("\n--- РАСШИФРОВАНИЕ ---")
        raw = input("Введите криптотекст: ")
        filtered = filter_alphabet(raw)
        print("Отфильтрованный криптотекст (только буквы):", filtered)
        if not filtered:
            print("Ошибка: криптотекст не содержит допустимых символов.")
            return
        key = input_key()
        decrypted = belazo_decrypt(filtered, key)
        print("Расшифрованный текст (буквы):", decrypted)
        restored = postprocess_decrypted(decrypted)
        print("Текст после замены зпт/тчк на знаки препинания:", restored)

    else:
        print("Неверный выбор. Возврат в главное меню.")

# =============================================================================
# 3. Шифр Виженера (самоключ + ключ-шифртекст)
# =============================================================================
def validate_key_char(key: str) -> bool:
    key = key.strip().lower()
    return len(key) == 1 and key[0] in ALPHABET

def input_key_char(prompt: str = "Введите ключевую букву: ") -> str:
    while True:
        key = input(prompt).strip().lower()
        if not key:
            print("Ключ не может быть пустым.")
            continue
        if len(key) != 1:
            print("Ключ должен состоять ровно из одной буквы. Использую первый символ.")
            key = key[0]
        if key in ALPHABET:
            return key
        else:
            print(f"Ошибка: буква '{key}' не входит в алфавит.")
            print("Допустимые символы:", ALPHABET)

# Самоключ по открытому тексту
def encrypt_autokey(plain: str, key_char: str) -> str:
    cipher = []
    prev_char = key_char
    for ch in plain:
        p = ALPHABET.index(ch)
        g = ALPHABET.index(prev_char)
        c = (p + g) % N
        cipher.append(ALPHABET[c])
        prev_char = ch
    return ''.join(cipher)

def decrypt_autokey(cipher: str, key_char: str) -> str:
    plain = []
    prev_char = key_char
    for ch in cipher:
        c = ALPHABET.index(ch)
        g = ALPHABET.index(prev_char)
        p = (c - g) % N
        p_char = ALPHABET[p]
        plain.append(p_char)
        prev_char = p_char
    return ''.join(plain)

# Ключ-шифртекст
def encrypt_cipher_autokey(plain: str, key_char: str) -> str:
    cipher = []
    prev_char = key_char
    for ch in plain:
        p = ALPHABET.index(ch)
        g = ALPHABET.index(prev_char)
        c = (p + g) % N
        c_char = ALPHABET[c]
        cipher.append(c_char)
        prev_char = c_char
    return ''.join(cipher)

def decrypt_cipher_autokey(cipher: str, key_char: str) -> str:
    plain = []
    # Первый символ
    first_c = ALPHABET.index(cipher[0])
    key = ALPHABET.index(key_char)
    first_p = (first_c - key) % N
    plain.append(ALPHABET[first_p])
    # Остальные
    for i in range(1, len(cipher)):
        c = ALPHABET.index(cipher[i])
        g = ALPHABET.index(cipher[i-1])
        p = (c - g) % N
        plain.append(ALPHABET[p])
    return ''.join(plain)

def vigenere_main():
    print("\n=== Шифр Виженера (два варианта) ===")
    print("Алфавит (32 буквы):", ALPHABET)
    print()
    print("Выберите режим:")
    print("1 - шифрование")
    print("2 - расшифрование")
    choice_mode = input("Ваш выбор (1/2): ").strip()
    if choice_mode not in ('1', '2'):
        print("Неверный выбор. Возврат в главное меню.")
        return

    print("\nВыберите тип шифра Виженера:")
    print("1 - с самоключом (autokey, гамма = ключ + открытый текст)")
    print("2 - с ключом-шифртекстом (ciphertext autokey, гамма = ключ + шифртекст)")
    choice_type = input("Ваш выбор (1/2): ").strip()
    if choice_type not in ('1', '2'):
        print("Неверный выбор. Возврат в главное меню.")
        return

    if choice_mode == '1':  # шифрование
        raw = input("\nВведите открытый текст: ")
        processed = preprocess_open_text(raw)
        print("Обработанный текст (только буквы, знаки -> зпт/тчк):", processed)
        if not processed:
            print("Ошибка: после обработки не осталось букв для шифрования.")
            return
        key_char = input_key_char("Введите ключевую букву: ")
        if choice_type == '1':
            encrypted = encrypt_autokey(processed, key_char)
            print("\nЗашифрованный текст (самоключ):", encrypted)
        else:
            encrypted = encrypt_cipher_autokey(processed, key_char)
            print("\nЗашифрованный текст (ключ-шифртекст):", encrypted)

    else:  # расшифрование
        raw = input("\nВведите криптотекст: ")
        filtered = filter_alphabet(raw)
        print("Отфильтрованный криптотекст (только буквы):", filtered)
        if not filtered:
            print("Ошибка: криптотекст не содержит допустимых символов.")
            return
        key_char = input_key_char("Введите ключевую букву: ")
        if choice_type == '1':
            decrypted = decrypt_autokey(filtered, key_char)
            print("\nРасшифрованный текст (буквы, самоключ):", decrypted)
        else:
            decrypted = decrypt_cipher_autokey(filtered, key_char)
            print("\nРасшифрованный текст (буквы, ключ-шифртекст):", decrypted)
        restored = postprocess_decrypted(decrypted)
        print("Текст после замены зпт/тчк на знаки препинания:", restored)

# =============================================================================
# 4. Шифр на основе S-блоков МАГМА (ГОСТ Р 34.12-2015)
# =============================================================================
# S-блоки ГОСТ (фиксированные)
PI = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

INV_PI = []
for tbl in PI:
    inv = [0] * 16
    for i, val in enumerate(tbl):
        inv[val] = i
    INV_PI.append(inv)

def _bytes_to_nibbles(block: bytes) -> list:
    nibbles = []
    for b in block:
        nibbles.append(b >> 4)
        nibbles.append(b & 0x0F)
    return nibbles

def _nibbles_to_bytes(nibbles: list) -> bytes:
    res = bytearray()
    for i in range(0, 8, 2):
        high = nibbles[i] << 4
        low = nibbles[i+1]
        res.append(high | low)
    return bytes(res)

def _rotl11(x: int) -> int:
    return ((x << 11) & 0xFFFFFFFF) | (x >> (32 - 11))

def _rotr11(x: int) -> int:
    return (x >> 11) | ((x & 0x7FF) << (32 - 11))

def apply_sbox_block(block: bytes) -> bytes:
    nibs = _bytes_to_nibbles(block)
    new_nibs = [PI[7-i][nibs[i]] for i in range(8)]
    val = int.from_bytes(_nibbles_to_bytes(new_nibs), byteorder='big')
    val = _rotl11(val)
    return val.to_bytes(4, byteorder='big')

def inverse_sbox_block(block: bytes) -> bytes:
    val = int.from_bytes(block, byteorder='big')
    val = _rotr11(val)
    tmp = val.to_bytes(4, byteorder='big')
    nibs = _bytes_to_nibbles(tmp)
    new_nibs = [INV_PI[7-i][nibs[i]] for i in range(8)]
    return _nibbles_to_bytes(new_nibs)

def pad_pkcs7(data: bytes) -> bytes:
    pad_len = 4 - (len(data) % 4)
    return data + bytes([pad_len] * pad_len)

def unpad_pkcs7(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 4:
        raise ValueError("Некорректный padding")
    return data[:-pad_len]

def encrypt_bytes(data: bytes) -> bytes:
    padded = pad_pkcs7(data)
    result = bytearray()
    for i in range(0, len(padded), 4):
        block = padded[i:i+4]
        enc_block = apply_sbox_block(block)
        result.extend(enc_block)
    return bytes(result)

def decrypt_bytes(data: bytes) -> bytes:
    if len(data) % 4 != 0:
        raise ValueError("Длина шифротекста должна быть кратна 4 байтам")
    result = bytearray()
    for i in range(0, len(data), 4):
        block = data[i:i+4]
        dec_block = inverse_sbox_block(block)
        result.extend(dec_block)
    return unpad_pkcs7(bytes(result))
def apply_sbox_only(block: bytes) -> bytes:
    nibs = _bytes_to_nibbles(block)               # разбиваем на полубайты
    new_nibs = [PI[7-i][nibs[i]] for i in range(8)] # применяем S-блоки
    return _nibbles_to_bytes(new_nibs)             # собираем обратно
def magma_main():
    print("\n=== S-блок замены ГОСТ Р 34.12-2015 (МАГМА) ===")
    print("Фиксированный набор подстановок (8 S-блоков) + циклический сдвиг 11 бит.")
    print("Работа с русским текстом: предобработка (зпт/тчк), кодировка UTF-8.")
    print()
    print("Выберите режим:")
    print("1 - шифрование открытого текста")
    print("2 - расшифрование криптотекста")
    print("3 - применить преобразование t к 32-битному блоку (тестовый режим)")
    choice = input("Ваш выбор (1/2/3): ").strip()

    if choice == '1':
        print("\n--- ШИФРОВАНИЕ ---")
        raw = input("Введите открытый текст: ")
        processed = preprocess_open_text(raw)
        if not processed:
            print("Ошибка: после обработки не осталось букв.")
            return
        print("Обработанный текст (только буквы, знаки -> зпт/тчк):", processed)
        data = processed.encode('utf-8')
        print(f"Исходные данные (UTF-8, {len(data)} байт): {data.hex().upper()}")
        encrypted = encrypt_bytes(data)
        print(f"Зашифрованные данные (hex): {encrypted.hex().upper()}")

    elif choice == '2':
        print("\n--- РАСШИФРОВАНИЕ ---")
        hex_input = input("Введите криптотекст в шестнадцатеричном виде: ").strip()
        try:
            encrypted = bytes.fromhex(hex_input)
        except ValueError:
            print("Ошибка: некорректная шестнадцатеричная строка.")
            return
        try:
            decrypted = decrypt_bytes(encrypted)
        except Exception as e:
            print(f"Ошибка расшифрования: {e}")
            return
        try:
            decoded = decrypted.decode('utf-8')
        except UnicodeDecodeError:
            print("Ошибка: не удалось декодировать результат в UTF-8.")
            return
        restored = postprocess_decrypted(decoded)
        print("Расшифрованный текст (после замены зпт/тчк):", restored)

    elif choice == '3':
        print("\n--- ПРЕОБРАЗОВАНИЕ t ---")
        hex_input = input("Введите 32-битное число в hex (8 символов): ").strip().replace(' ', '')
        if len(hex_input) != 8:
            print("Ошибка: нужно ровно 8 шестнадцатеричных символов.")
            return
        try:
            data = bytes.fromhex(hex_input)
        except ValueError:
            print("Ошибка: некорректная шестнадцатеричная строка.")
            return
        # Применяем только подстановку S-блоков (без сдвига)
        result = apply_sbox_only(data)
        print(f"Результат преобразования t: {result.hex().upper()}")

    else:
        print("Неверный выбор. Возврат в главное меню.")
# =============================================================================
# Главное меню
# =============================================================================
def main_menu():
    while True:
        print("\n" + "="*50)
        print("ГЛАВНОЕ МЕНЮ")
        print("="*50)
        print("1 - Шифр Тритемия")
        print("2 - Шифр Белазо (Виженер с ключевым словом)")
        print("3 - Шифр Виженера (самоключ / ключ-шифртекст)")
        print("4 - Шифр на основе S-блоков МАГМА")
        print("0 - Завершение работы")
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            trithemius_main()
        elif choice == '2':
            belazo_main()
        elif choice == '3':
            vigenere_main()
        elif choice == '4':
            magma_main()
        elif choice == '0':
            print("Работа завершена.")
            break
        else:
            print("Неверный ввод. Пожалуйста, выберите 0-4.")

if __name__ == "__main__":
    main_menu()