import sys
from itertools import zip_longest

list_alph = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф",
             "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]


def digitization(open_text):
    dig_text = ""
    for i in range(len(open_text)):
        cipher = list_alph.index(open_text[i])
        dig_text += format(cipher, '05b')
    return dig_text


def undigitization(d_text):
    def grouper(n, iterable, fill_value=None):
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fill_value, *args)
    d_text = ' '.join(''.join(g) for g in grouper(5, d_text, ''))
    d_array = d_text.split()
    open_text = ""
    for i in d_array:
        open_text += list_alph[int(str(int(i)), 2)]
    return open_text


def generate_gamma(key, frame_num):
    rx = [0] * 19
    ry = [0] * 22
    rz = [0] * 23

    # ШАГ 1 — загрузка ключа (64 такта)
    # feedback = rx[0], новый бит добавляется СПРАВА
    for i in range(64):
        fx = rx[0]
        fy = ry[0]
        fz = rz[0]
        rx = rx[1:] + [fx ^ int(key[i])]
        ry = ry[1:] + [fy ^ int(key[i])]
        rz = rz[1:] + [fz ^ int(key[i])]

    # ШАГ 2 — загрузка номера кадра (22 такта)
    frame_bits = format(frame_num, '022b')
    for i in range(22):
        fx = rx[0]
        fy = ry[0]
        fz = rz[0]
        rx = rx[1:] + [fx ^ int(frame_bits[i])]
        ry = ry[1:] + [fy ^ int(frame_bits[i])]
        rz = rz[1:] + [fz ^ int(frame_bits[i])]

    # ШАГ 3 — 100 тактов перемешивания (stop-and-go)
    for _ in range(100):
        majority = (rx[8] + ry[10] + rz[10]) > 1

        if rx[8] == majority:
            new_bit = rx[13] ^ rx[16] ^ rx[17] ^ rx[18]
            rx = rx[1:] + [new_bit]

        if ry[10] == majority:
            new_bit = ry[20] ^ ry[21]
            ry = ry[1:] + [new_bit]

        if rz[10] == majority:
            new_bit = rz[7] ^ rz[20] ^ rz[21] ^ rz[22]
            rz = rz[1:] + [new_bit]

    # ШАГ 4 — генерация гаммы (114 тактов)
    # ✅ Гамма берётся ДО сдвига регистров
    key_stream = []
    for _ in range(114):
        majority = (rx[8] + ry[10] + rz[10]) > 1

        key_stream.append(rx[18] ^ ry[21] ^ rz[22])  # ← гамма ДО сдвига

        if rx[8] == majority:
            new_bit = rx[13] ^ rx[16] ^ rx[17] ^ rx[18]
            rx = rx[1:] + [new_bit]

        if ry[10] == majority:
            new_bit = ry[20] ^ ry[21]
            ry = ry[1:] + [new_bit]

        if rz[10] == majority:
            new_bit = rz[7] ^ rz[20] ^ rz[21] ^ rz[22]
            rz = rz[1:] + [new_bit]

    return key_stream


def decryption_format(dec_text):
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace('прб', ' ')
    result = dec_text[0].upper() + dec_text[1:]
    result_list = list(result)
    for i in range(len(result_list) - 3):
        if result_list[i] == ".":
            result_list[i + 2] = result_list[i + 2].upper()
    result = ""
    for char in result_list:
        result += char
    return result


def get_key():
    print("Выберите тип ключа:")
    print("  1. Ввести 64 бита (0 и 1)")
    print("  2. Ввести 8 русских букв")
    key_type = input("Ваш выбор: ").strip()

    if key_type == "1":
        key = input("Введите 64-битный ключ: ").strip()
        if len(key) != 64 or not all(c in '01' for c in key):
            print("Неправильный ключ! Нужно ровно 64 символа (0 или 1)")
            exit()
        return key

    elif key_type == "2":
        key_word = input("Введите ключ (8 русских букв): ").strip().lower()
        for ch in key_word:
            if ch not in list_alph:
                print("Неправильный ключ! Только русские буквы (без Ё)")
                exit()
        if len(key_word) < 8:
            print("Нужно минимум 8 букв!")
            exit()
        if len(key_word) > 8:
            key_word = key_word[:8]
        key = ''.join(format(b, '08b') for b in key_word.encode('utf-8'))
        key = key[:64]
        print(f"Ключ в битах: {key}")
        return key
    else:
        print("Неверный выбор!")
        exit()


def A5_1(operation, text):
    key = get_key()
    num = 0

    if operation == 1:
        ciphertext = ""
        binary = list(digitization(text))

        while len(binary) > 0:
            keystream = generate_gamma(key, num)
            for j in range(114 if len(binary) > 114 else len(binary)):
                ciphertext += str(int(binary[j]) ^ int(keystream[j]))
            binary = binary[114:]
            num += 1

        print("Encrypted text:", ' '.join(ciphertext[i: i + 5] for i in range(0, len(ciphertext), 5)))
        print()

    if operation == 2:
        dec_text = ""

        while len(text) > 0:
            binary_xor = []
            keystream = generate_gamma(key, num)
            for i in range(114 if len(text) > 114 else len(text)):
                binary_xor.insert(i, int(text[i]))
                dec_text += str(binary_xor[i] ^ keystream[i])
            text = text[114:]
            num += 1

        analog = undigitization(dec_text)
        answer = decryption_format(analog)
        print("Decrypted text:", end=' ')
        for i in answer:
            print(i, end='')
        print()


while True:
    print("""Select a cipher:
             1.  A5/1
             2.  Exit
         """)
    select: int = int(input())
    if select == 2:
        sys.exit()
    if select not in [1, 2]:
        print("Wrong select!")
        continue

    print(""" Select an action:
                1. Encryption
                2. Decryption""")
    operation: int = int(input())
    if operation not in [1, 2]:
        print("Wrong select!")
        continue

    text: str = str(input('Enter text: '))
    print()

    if operation == 1:
        for i in range(len(text)):
            if text.find('.') != -1:
                index = text.find('.')
                text = text[:index] + 'тчк' + text[index + 1:]
            if text.find(',') != -1:
                index = text.find(',')
                text = text[:index] + 'зпт' + text[index + 1:]
            if text.find(' ') != -1:
                index = text.find(' ')
                text = text[:index] + 'прб' + text[index + 1:]
    else:
        text = text.replace(' ', '')

    if select == 1:
        A5_1(operation, text.lower())
        print()
