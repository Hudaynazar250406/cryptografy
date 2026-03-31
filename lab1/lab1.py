# Алфавит и замены знаков препинания

# Русский алфавит БЕЗ Ё (32 буквы)
alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ALPHABET_LEN = len(alphabet)  # 32
reversed_alphabet = alphabet[::-1]

punctuation_map = {
    '.': ' тчк ',
    ',': ' зпт ',
    '!': ' вст ',
    '?': ' впр ',
    ':': ' двт ',
    ';': ' тчкзпт ',
    '"': ' кав ',
    '-': ' тир ',
}

# Словарь обратной замены
reverse_punctuation_map = {v.strip(): k for k, v in punctuation_map.items()}


def replace_punctuation(text: str) -> str:
    for punct, word in punctuation_map.items():
        text = text.replace(punct, word)
    return text


def restore_punctuation(text: str) -> str:
    for word, punct in reverse_punctuation_map.items():
        text = text.replace(word, punct)
    return text


# Реализация шифров

def atbash_cipher(text: str) -> str:
    trans_table = str.maketrans(
        alphabet + alphabet.lower(),
        reversed_alphabet + reversed_alphabet.lower()
    )
    return text.translate(trans_table)


def caesar_cipher(text: str, shift: int) -> str:
    # Нормализуем сдвиг по длине алфавита (32)
    shift = shift % ALPHABET_LEN
    result = ''
    for char in text:
        if char.isupper():
            idx = alphabet.find(char)
            if idx != -1:
                new_idx = (idx + shift) % ALPHABET_LEN
                result += alphabet[new_idx]
            else:
                result += char
        elif char.islower():
            idx = alphabet.lower().find(char)
            if idx != -1:
                new_idx = (idx + shift) % ALPHABET_LEN
                result += alphabet[new_idx].lower()
            else:
                result += char
        else:
            result += char
    return result


def create_polybius_square():
    size = 6
    square = {}
    reverse_square = {}
    extended_alphabet = alphabet + ' '
    for i, letter in enumerate(extended_alphabet):
        row = i // size
        col = i % size
        key = f"{row + 1}{col + 1}"
        square[letter] = key
        reverse_square[key] = letter
    return square, reverse_square


def polybius_encrypt(text: str) -> str:
    square, _ = create_polybius_square()
    result = ''
    for char in text:
        upper_char = char.upper()
        if upper_char in square:
            result += square[upper_char] + ' '
        else:
            result += char + ' '
    return result.strip()


def polybius_decrypt(text: str) -> str:
    _, reverse_square = create_polybius_square()
    pairs = text.split()
    result = ''
    for pair in pairs:
        if pair.isdigit() and pair in reverse_square:
            result += reverse_square[pair]
        else:
            result += pair
    return result


# Основной цикл

while True:
    print("\n1 - Зашифровать | 2 - Расшифровать | exit - выйти")
    action = input("Выберите: ").strip()

    if action == 'exit':
        print("Выход.")
        break

    if action not in ['1', '2']:
        print("Неверный выбор.")
        continue

    print("1 - Атбаш | 2 - Цезарь | 3 - Полибий")
    cipher = input("Выберите шифр: ").strip()

    if cipher not in ['1', '2', '3']:
        print("Неверный шифр.")
        continue

    text = input("Введите текст (Enter для окончания): ").strip()

    # ЗАШИФРОВАТЬ
    if action == '1':
        processed_text = replace_punctuation(text)

        if cipher == '1':
            result = atbash_cipher(processed_text)

        elif cipher == '2':
            try:
                key = int(input("Введите ключ (целое число): "))
            except ValueError:
                print("Ошибка: ключ должен быть целым числом.")
                continue

            # Запрещаем ключи, кратные 32
            if key % ALPHABET_LEN == 0:
                print(
                    f"Ошибка: ключ {key} недопустим, так как (ключ % {ALPHABET_LEN}) = 0. "
                    f"Выберите другой ключ."
                )
                continue

            result = caesar_cipher(processed_text, key)

        elif cipher == '3':
            result = polybius_encrypt(processed_text)

        print("Результат:", result)

    # РАСШИФРОВАТЬ
    elif action == '2':
        if cipher == '1':
            result = atbash_cipher(text)

        elif cipher == '2':
            try:
                key = int(input("Введите ключ (целое число): "))
            except ValueError:
                print("Ошибка: ключ должен быть целым числом.")
                continue

            if key % ALPHABET_LEN == 0:
                print(
                    f"Ошибка: ключ {key} недопустим, так как (ключ % {ALPHABET_LEN}) = 0. "
                    f"Выберите другой ключ."
                )
                continue

            # Для расшифровки используем отрицательный сдвиг
            result = caesar_cipher(text, -key)

        elif cipher == '3':
            result = polybius_decrypt(text)

        result = restore_punctuation(result)
        print("Результат:", result)
