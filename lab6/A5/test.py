import sys
from itertools import zip_longest


list_alph = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф",
             "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]


def digitization(open_text):
    dig_text = ""
    for i in range(len(open_text)):
        cipher = (list_alph.index(open_text[i]))
        cipher = int(cipher)
        dig_text += (format(cipher, '05b'))
    return dig_text


def undigitization(d_text):
    def grouper(n, iterable, fill_value=None):
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fill_value, *args)

    d_text = ' '.join(''.join(g) for g in grouper(5, d_text, ''))
    d_array = d_text.split()
    open_text = ""

    for i in d_array: open_text += (list_alph[int(str(int(i)), 2)])

    return open_text


def generate_gamma(key, frame_num):

########################_REGISTERS_LOADING_########################

    register_x = []
    register_y = []
    register_z = []

    reg_x_length = 19
    reg_y_length = 22
    reg_z_length = 23

    for i in range(reg_x_length):
        register_x.append(int(key[i]))

    for j in range(reg_y_length):
        register_y.append(int(key[j]))

    for k in range(reg_z_length):
        register_z.append(int(key[k]))

#######################_REGISTERS_PREPARATING_#######################

    queue_x = key[19:] + (format(frame_num, '022b'))
    queue_y = key[22:] + (format(frame_num, '022b'))
    queue_z = key[23:] + (format(frame_num, '022b'))

    while len(queue_x) > 0:
        new_bit = register_x[0] ^ int(queue_x[0])
        register_x = register_x[1:] + [new_bit]
        queue_x = queue_x[1:]

    while len(queue_y) > 0:
        new_bit = register_y[0] ^ int(queue_y[0])
        register_y = register_y[1:] + [new_bit]
        queue_y = queue_y[1:]

    while len(queue_z) > 0:
        new_bit = register_z[0] ^ int(queue_z[0])
        register_z = register_z[1:] + [new_bit]
        queue_z = queue_z[1:]

    for _ in range(100):
        new_bit = register_x[13] ^ register_x[16] ^ register_x[17] ^ register_x[18]
        register_x = register_x[1:] + [new_bit]

        new_bit = register_y[20] ^ register_y[21]
        register_y = register_y[1:] + [new_bit]

        new_bit = register_z[7] ^ register_z[20] ^ register_z[21] ^ register_z[22]
        register_z = register_z[1:] + [new_bit]

############################_GAMMA_GENERATE_############################

    key_stream = []

    for _ in range(114):

        majority = (register_x[8] + register_y[10] + register_z[10]) > 1

        if register_x[8] == majority:
            new_bit = register_x[13] ^ register_x[16] ^ register_x[17] ^ register_x[18]
            register_x = [new_bit] + register_x[:-1]

        if register_y[10] == majority:
            new_bit = register_y[20] ^ register_y[21]
            register_y = [new_bit] + register_y[:-1]

        if register_z[10] == majority:
            new_bit = register_z[7] ^ register_z[20] ^ register_z[21] ^ register_z[22]
            register_z = [new_bit] + register_z[:-1]

        key_stream.append(register_x[18] ^ register_y[21] ^ register_z[22])

    return key_stream


def decryption_format(dec_text):
    dec_text = dec_text.replace('тчк', '.').replace('зпт', ',').replace('прб', ' ')
    result = dec_text[0].upper() + dec_text[1:]
    result_list = list(result)
    for i in range(len(result_list) - 3):
        if result_list[i] == ".":
            result_list[i + 2] = result_list[i + 2].upper()

    result = ""
    for char in result_list: result += char

    return result


def A5_1(operation, text):

    key = str(input('Enter a 64-bit key: '))
    if len(key) != 64:
        print("Wrong key")
        exit()

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

        print("Encrypted text: ", ' '.join(ciphertext[i: i + 5] for i in range(0, len(ciphertext), 5)))
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

        print("Decrypted text: ", end=' ')
        for i in answer: print(i, end='')
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
                str1_split1 = text[:index]
                str1_split2 = text[index + 1:]
                text = str1_split1 + 'тчк' + str1_split2

            if text.find(',') != -1:
                index = text.find(',')
                str1_split1 = text[:index]
                str1_split2 = text[index + 1:]
                text = str1_split1 + 'зпт' + str1_split2

            if text.find(' ') != -1:
                index = text.find(' ')
                str1_split1 = text[:index]
                str1_split2 = text[index + 1:]
                text = str1_split1 + 'прб' + str1_split2

    else:
        text = text.replace(' ', '')

    if select == 1:
        A5_1(operation, text.lower())
        print()
