#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

list_alph = ["а","б","в","г","д","е","ж","з","и","й","к","л","м","н","о","п","р","с","т","у","ф",
             "х","ц","ч","ш","щ","ъ","ы","ь","э","ю","я"]


# ══════════════════════════ РЕГИСТРЫ A5/2 ══════════════════════════

class A52Cipher:
    def __init__(self):
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.R4 = [0] * 17

    def majority(self, x, y, z):
        return (x & y) | (x & z) | (y & z)

    def clock_all(self, input_bit):
        nb1 = self.R1[0] ^ self.R1[14] ^ self.R1[17] ^ self.R1[18] ^ input_bit
        self.R1 = [nb1] + self.R1[:-1]
        nb2 = self.R2[0] ^ self.R2[21] ^ input_bit
        self.R2 = [nb2] + self.R2[:-1]
        nb3 = self.R3[0] ^ self.R3[8] ^ self.R3[21] ^ self.R3[22] ^ input_bit
        self.R3 = [nb3] + self.R3[:-1]
        nb4 = self.R4[0] ^ self.R4[12] ^ input_bit
        self.R4 = [nb4] + self.R4[:-1]

    def clock_stop_go(self, generate_output=False):
        f = self.majority(self.R4[3], self.R4[7], self.R4[10])
        shift_r1 = (self.R4[10] == f)
        shift_r2 = (self.R4[3]  == f)
        shift_r3 = (self.R4[7]  == f)

        nb4 = self.R4[0] ^ self.R4[12]
        self.R4 = [nb4] + self.R4[:-1]

        if shift_r1:
            nb1 = self.R1[0] ^ self.R1[14] ^ self.R1[17] ^ self.R1[18]
            self.R1 = [nb1] + self.R1[:-1]
        if shift_r2:
            nb2 = self.R2[0] ^ self.R2[21]
            self.R2 = [nb2] + self.R2[:-1]
        if shift_r3:
            nb3 = self.R3[0] ^ self.R3[8] ^ self.R3[21] ^ self.R3[22]
            self.R3 = [nb3] + self.R3[:-1]

        if generate_output:
            out  = self.R1[18] ^ self.R2[21] ^ self.R3[22]
            maj1 = self.majority(self.R1[12], self.R1[14], self.R1[15])
            maj2 = self.majority(self.R2[9],  self.R2[13], self.R2[16])
            maj3 = self.majority(self.R3[13], self.R3[16], self.R3[18])
            return out ^ maj1 ^ maj2 ^ maj3
        return None

    def initialize(self, key_bits, frame_bits):
        self.R1 = [0]*19; self.R2 = [0]*22
        self.R3 = [0]*23; self.R4 = [0]*17
        for b in key_bits:
            self.clock_all(b)
        for b in frame_bits:
            self.clock_all(b)
        self.R4[3] = 1; self.R4[7] = 1; self.R4[10] = 1
        for _ in range(99):
            self.clock_stop_go(generate_output=False)

    def generate_keystream(self, length):
        ks = []
        for _ in range(length):
            ks.append(self.clock_stop_go(generate_output=True))
        return ks


# ══════════════════════════ КОДИРОВАНИЕ ══════════════════════════

def digitization(text):
    """Текст → биты (5 бит на букву)"""
    bits = []
    for ch in text:
        idx = list_alph.index(ch)
        bits += [int(b) for b in format(idx, '05b')]
    return bits

def undigitization(bits):
    """Биты → текст (каждые 5 бит = 1 буква)"""
    while len(bits) % 5 != 0:
        bits.append(0)
    text = ""
    for i in range(0, len(bits), 5):
        idx = int(''.join(str(b) for b in bits[i:i+5]), 2)
        if idx < len(list_alph):
            text += list_alph[idx]
    return text

def xor_bits(a, b):
    return [x ^ y for x, y in zip(a, b)]

def bits_str(bits):
    """Биты в строку"""
    return ''.join(str(b) for b in bits)

def bits_group5(bits):
    """Биты → строка с пробелами каждые 5 (= 1 буква)"""
    s = bits_str(bits)
    return ' '.join(s[i:i+5] for i in range(0, len(s), 5))


# ══════════════════════════ ВВОД КЛЮЧА И КАДРА ══════════════════════════

def get_key():
    print("\nТип ключа:")
    print("  1. Строка из 64 бит (0 и 1)")
    print("  2. 8 русских букв")
    choice = input("Выбор: ").strip()

    if choice == "1":
        key = input("Введите 64 бита: ").strip()
        if len(key) != 64 or not all(c in '01' for c in key):
            print("❌ Нужно ровно 64 символа (0 или 1)!")
            sys.exit(1)
        return [int(b) for b in key]

    elif choice == "2":
        word = input("Введите 8 русских букв: ").strip().lower()
        for ch in word:
            if ch not in list_alph:
                print(f"❌ Символ '{ch}' не в алфавите (без Ё)!")
                sys.exit(1)
        if len(word) < 8:
            print("❌ Нужно минимум 8 букв!")
            sys.exit(1)
        word = word[:8]
        key_bits = []
        for ch in word:
            key_bits += [int(b) for b in format(list_alph.index(ch), '08b')]
        print(f"Ключ в битах: {bits_str(key_bits)}")
        return key_bits
    else:
        print("❌ Неверный выбор!"); sys.exit(1)


def get_frame():
    print("\nТип номера кадра:")
    print("  1. Число (0–4194303)")
    print("  2. Строка из 22 бит")
    choice = input("Выбор: ").strip()

    if choice == "1":
        try:
            n = int(input("Номер кадра: ").strip()) & 0x3FFFFF
        except:
            n = 0
        bits = [(n >> i) & 1 for i in range(22)]
        print(f"Кадр в битах: {bits_str(bits)}")
        return bits

    elif choice == "2":
        s = input("Введите 22 бита кадра: ").strip()
        if len(s) != 22 or not all(c in '01' for c in s):
            print("❌ Нужно ровно 22 бита!"); sys.exit(1)
        return [int(b) for b in s]
    else:
        print("❌ Неверный выбор!"); sys.exit(1)


# ══════════════════════════ ШИФРОВАНИЕ ══════════════════════════

def encrypt_mode():
    print("\n" + "="*65)
    print("              ШИФРОВАНИЕ A5/2")
    print("="*65)

    text = input("Текст (русские буквы): ").strip().lower()
    text = text.replace('.','тчк').replace(',','зпт').replace(' ','прб')
    for ch in text:
        if ch not in list_alph:
            print(f"❌ Символ '{ch}' не поддерживается!"); return

    key_bits   = get_key()
    frame_bits = get_frame()

    plain_bits = digitization(text)
    n_letters  = len(text)
    n_bits     = len(plain_bits)  # = n_letters * 5

    print(f"\n{'─'*65}")
    print(f"Открытый текст : '{text}'  ({n_letters} букв = {n_bits} бит)")
    print()

    # Побуквенная таблица кодирования
    print(f"  {'Буква':<8} {'Индекс':<8} {'5 бит'}")
    print(f"  {'─'*30}")
    for ch in text:
        idx = list_alph.index(ch)
        print(f"  {ch:<8} {idx:<8} {format(idx,'05b')}")

    print(f"\nБиты открытого текста: {bits_group5(plain_bits)}")

    # Генерация гаммы и шифрование
    bits_left       = plain_bits[:]
    ciphertext_bits = []
    keystream_all   = []

    while bits_left:
        c = A52Cipher()
        c.initialize(key_bits, frame_bits)
        ks    = c.generate_keystream(min(114, len(bits_left)))
        chunk = bits_left[:114]
        enc   = xor_bits(chunk, ks)
        ciphertext_bits += enc
        keystream_all   += ks[:len(chunk)]
        bits_left = bits_left[114:]

    # ─── ГЛАВНАЯ ТАБЛИЦА ───
    print(f"\n{'─'*65}")
    print("ТАБЛИЦА ШИФРОВАНИЯ (5 бит = 1 буква):")
    print(f"\n  {'№':<5} {'Буква':<7} {'Открытый':<10} {'Гамма':<10} {'Шифр':<10}")
    print(f"  {'─'*45}")

    for i, ch in enumerate(text):
        start = i * 5
        p_bits = plain_bits[start:start+5]
        k_bits = keystream_all[start:start+5]
        c_bits = ciphertext_bits[start:start+5]

        p_s = bits_str(p_bits)
        k_s = bits_str(k_bits)
        c_s = bits_str(c_bits)

        print(f"  {i+1:<5} '{ch}'     {p_s:<10} {k_s:<10} {c_s:<10}")

        # побитовый XOR
        for bit_i in range(5):
            p = p_bits[bit_i]
            k = k_bits[bit_i]
            c = c_bits[bit_i]
            print(f"  {'':5} бит {start+bit_i+1:<3}  {p:<10} {k:<10} {c}")
        print()

    print(f"{'─'*65}")
    print(f"Гамма      : {bits_group5(keystream_all)}")
    print(f"Шифртекст  : {bits_group5(ciphertext_bits)}")
    print(f"{'─'*65}")
    print(f"Гамма      (сплошная): {bits_str(keystream_all)}")
    print(f"Шифртекст  (сплошная): {bits_str(ciphertext_bits)}")

    save = input("\nСохранить в файл? (y/n): ").strip().lower()
    if save == 'y':
        fname = input("Имя файла (Enter=cipher_a52.txt): ").strip() or "cipher_a52.txt"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(f"Key:        {bits_str(key_bits)}\n")
            f.write(f"Frame:      {bits_str(frame_bits)}\n")
            f.write(f"PlainText:  {text}\n")
            f.write(f"PlainBits:  {bits_group5(plain_bits)}\n")
            f.write(f"Gamma:      {bits_group5(keystream_all)}\n")
            f.write(f"CipherBits: {bits_str(ciphertext_bits)}\n")
        print(f"✅ Сохранено в '{fname}'")


# ══════════════════════════ ДЕШИФРОВАНИЕ ══════════════════════════

def decrypt_mode():
    print("\n" + "="*65)
    print("              ДЕШИФРОВАНИЕ A5/2")
    print("="*65)

    key_bits   = get_key()
    frame_bits = get_frame()

    print("\nФормат шифртекста:")
    print("  1. Биты (строка из 0 и 1, пробелы допустимы)")
    print("  2. Файл (cipher_a52.txt)")
    fmt_choice = input("Выбор (1/2): ").strip()

    cipher_bits = []
    if fmt_choice == "1":
        s = input("Биты: ").strip().replace(' ', '')
        cipher_bits = [int(c) for c in s if c in '01']
    elif fmt_choice == "2":
        fname = input("Имя файла: ").strip()
        try:
            with open(fname, encoding='utf-8') as f:
                for line in f:
                    if line.startswith("CipherBits:"):
                        s = line.split(":",1)[1].strip().replace(' ','')
                        cipher_bits = [int(c) for c in s if c in '01']
                        break
        except Exception as e:
            print(f"❌ Ошибка: {e}"); return
    else:
        print("❌ Неверный выбор!"); return

    if not cipher_bits:
        print("❌ Шифртекст пустой!"); return

    bits_left     = cipher_bits[:]
    plain_bits    = []
    keystream_all = []

    while bits_left:
        c = A52Cipher()
        c.initialize(key_bits, frame_bits)
        ks    = c.generate_keystream(min(114, len(bits_left)))
        chunk = bits_left[:114]
        dec   = xor_bits(chunk, ks)
        plain_bits    += dec
        keystream_all += ks[:len(chunk)]
        bits_left = bits_left[114:]

    n_letters = len(plain_bits) // 5

    # ─── ГЛАВНАЯ ТАБЛИЦА ───
    print(f"\n{'─'*65}")
    print("ТАБЛИЦА ДЕШИФРОВАНИЯ (5 бит = 1 буква):")
    print(f"\n  {'№':<5} {'Шифр':<10} {'Гамма':<10} {'Открытый':<10} {'Буква'}")
    print(f"  {'─'*50}")

    decoded = undigitization(plain_bits[:])

    for i in range(n_letters):
        start  = i * 5
        c_bits = cipher_bits[start:start+5]
        k_bits = keystream_all[start:start+5]
        p_bits = plain_bits[start:start+5]
        ch     = decoded[i] if i < len(decoded) else '?'

        c_s = bits_str(c_bits)
        k_s = bits_str(k_bits)
        p_s = bits_str(p_bits)

        print(f"  {i+1:<5} {c_s:<10} {k_s:<10} {p_s:<10} '{ch}'")

        for bit_i in range(5):
            c = c_bits[bit_i]
            k = k_bits[bit_i]
            p = p_bits[bit_i]
            print(f"  {'':5} бит {start+bit_i+1:<3}  {c:<10} {k:<10} {p}")
        print()

    print(f"{'─'*65}")
    print(f"Гамма      : {bits_group5(keystream_all)}")
    print(f"Шифртекст  : {bits_group5(cipher_bits)}")
    print(f"Открытый   : {bits_group5(plain_bits)}")

    result = decoded
    if result:
        result = result[0].upper() + result[1:]
    print(f"\n>>> РАСШИФРОВАНО: '{result}' <<<")


# ══════════════════════════ ГЛАВНОЕ МЕНЮ ══════════════════════════

def main():
    print("="*65)
    print("        АЛГОРИТМ A5/2 (GSM) — ШИФРОВАНИЕ/ДЕШИФРОВАНИЕ")
    print("="*65)
    while True:
        print("\nМЕНЮ:")
        print("  1. Шифрование")
        print("  2. Дешифрование")
        print("  0. Выход")
        choice = input("\nВыбор: ").strip()
        if choice == "0":
            print("До свидания!"); sys.exit(0)
        elif choice == "1":
            encrypt_mode()
        elif choice == "2":
            decrypt_mode()
        else:
            print("❌ Неверный выбор!")

if __name__ == "__main__":
    main()
