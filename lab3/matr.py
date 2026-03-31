# -*- coding: utf-8 -*-
import fractions  # для точных дробных вычислений

# ========================== НАСТРОЙКИ ==========================
START_INDEX = 1          # 1 если а=1, я=32
OUTPUT_DIGITS = 3        # количество цифр для каждого числа (здесь 3)
# ===============================================================

# Алфавит (32 буквы)
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

# Построение словарей в зависимости от START_INDEX
if START_INDEX == 1:
    char_to_num = {ch: i+1 for i, ch in enumerate(ALPHABET)}
    num_to_char = {i+1: ch for i, ch in enumerate(ALPHABET)}
else:
    char_to_num = {ch: i for i, ch in enumerate(ALPHABET)}
    num_to_char = {i: ch for i, ch in enumerate(ALPHABET)}

# ================== Функции для работы с матрицами (обычная арифметика) ==================
def determinant(matrix):
    """Вычисляет определитель квадратной матрицы (целочисленный)."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    det = 0
    for c in range(n):
        sub = [row[:c] + row[c+1:] for row in matrix[1:]]
        det += ((-1)**c) * matrix[0][c] * determinant(sub)
    return det

def matrix_minor(matrix, i, j):
    """Возвращает минор элемента (i,j) (матрица без i-й строки и j-го столбца)."""
    return [row[:j] + row[j+1:] for row in (matrix[:i] + matrix[i+1:])]

def matrix_cofactor(matrix):
    """Вычисляет матрицу кофакторов (алгебраических дополнений)."""
    n = len(matrix)
    cof = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = matrix_minor(matrix, i, j)
            cof[i][j] = ((-1)**(i+j)) * determinant(minor)
    return cof

def matrix_transpose(matrix):
    """Транспонирование матрицы."""
    return [list(row) for row in zip(*matrix)]

def matrix_inv(matrix):
    """
    Вычисляет обратную матрицу (точные дроби) для целочисленной квадратной матрицы.
    Возвращает список списков fractions.Fraction.
    """
    det = determinant(matrix)
    if det == 0:
        raise ValueError("Матрица вырождена, обратной не существует")
    cofactor = matrix_cofactor(matrix)
    adjugate = matrix_transpose(cofactor)  # присоединённая
    n = len(matrix)
    inv = [[fractions.Fraction(adjugate[i][j], det) for j in range(n)] for i in range(n)]
    return inv

# ================== Функции подготовки текста ==================
def prepare_text(original):
    result = []
    for ch in original.lower():
        if ch == ',':
            result.append('зпт')
        elif ch == '.':
            result.append('тчк')
        elif ch == ' ':
            continue
        elif ch in char_to_num:
            result.append(ch)
        # остальные символы игнорируем
    return ''.join(result)

def text_to_numbers(text):
    return [char_to_num[ch] for ch in text]

def numbers_to_text(nums):
    return ''.join(num_to_char[n] for n in nums)

# ================== Шифрование (без модуля) ==================
def encrypt(plain, key):
    n = len(key)
    plain_nums = text_to_numbers(plain)
    original_len = len(plain_nums)
    if original_len == 0:
        return [], 0

    # Дополнение последним символом исходного текста до кратности n
    if len(plain_nums) % n != 0:
        last_char_num = plain_nums[-1]
        while len(plain_nums) % n != 0:
            plain_nums.append(last_char_num)

    cipher_nums = []
    for i in range(0, len(plain_nums), n):
        block = plain_nums[i:i+n]
        new_block = [0]*n
        for row in range(n):
            s = 0
            for col in range(n):
                s += key[row][col] * block[col]
            # без модуля
            cipher_nums.append(s)
    return cipher_nums, original_len

# ================== Расшифрование (с дробной обратной матрицей) ==================
def decrypt(cipher_nums, key_inv, original_len):
    n = len(key_inv)
    # Проверка, что длина кратна n
    if len(cipher_nums) % n != 0:
        raise ValueError("Длина шифртекста не кратна размеру матрицы")

    plain_nums = []
    for i in range(0, len(cipher_nums), n):
        block = cipher_nums[i:i+n]
        new_block = [0]*n
        for row in range(n):
            s = fractions.Fraction(0, 1)
            for col in range(n):
                s += key_inv[row][col] * block[col]
            # Проверяем, что результат целый (можно округлить)
            if s.denominator != 1:
                # из-за возможных погрешностей, но в идеале должно быть целым
                # округлим до ближайшего целого
                val = int(round(float(s)))
            else:
                val = s.numerator
            new_block[row] = val
        plain_nums.extend(new_block)

    plain_nums = plain_nums[:original_len]
    # Если START_INDEX == 1, то числа уже в нужном диапазоне (они изначально были от 1 до 32)
    plain_text = numbers_to_text(plain_nums)
    plain_text = plain_text.replace('зпт', ',').replace('тчк', '.')
    return plain_text

# ================== Ввод матрицы ==================
def input_matrix():
    while True:
        try:
            n = int(input("Введите размер матрицы (n >= 3): "))
            if n < 3:
                print("Размер должен быть не меньше 3.")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число.")

    print(f"Введите матрицу {n}x{n} построчно, элементы через пробел (целые числа):")
    matrix = []
    for i in range(n):
        while True:
            row_str = input(f"Строка {i+1}: ").strip()
            try:
                row = list(map(int, row_str.split()))
                if len(row) != n:
                    print(f"Нужно ровно {n} чисел.")
                    continue
                matrix.append(row)
                break
            except ValueError:
                print("Ошибка: введите целые числа через пробел.")

    # Проверка невырожденности
    try:
        det = determinant(matrix)
        if det == 0:
            print("Определитель равен 0, матрица вырождена. Расшифрование будет невозможно.")
            yn = input("Продолжить с этой матрицей? (y/n): ").lower()
            if yn != 'y':
                return input_matrix()
        else:
            print(f"Определитель = {det}")
    except Exception as e:
        print(f"Ошибка: {e}")
        return input_matrix()

    return matrix

# ================== Основная программа ==================
def main():
    print("========== Матричный шифр (без модуля) ==========")
    print(f"Алфавит: {ALPHABET}")
    print(f"Нумерация: {START_INDEX}..{START_INDEX+31}")
    print(f"Формат чисел в строке: {OUTPUT_DIGITS} знака (с ведущими нулями)")
    print("="*40)

    # Выбор матрицы
    print("Источник матрицы-ключа:")
    print("1. Фиксированная 3x3 (из примера)")
    print("2. Ввести свою матрицу")
    choice = input("Выберите (1/2): ").strip()

    if choice == '1':
        KEY = [
            [1, 4, 8],
            [3, 7, 2],
            [6, 9, 5]
        ]
        print("Фиксированная матрица (из методички):")
        for row in KEY:
            print(row)
    else:
        KEY = input_matrix()
        print("Ваша матрица:")
        for row in KEY:
            print(row)

    # Вычисление обратной матрицы (точные дроби)
    try:
        KEY_INV = matrix_inv(KEY)
        print("Обратная матрица (в виде дробей):")
        for row in KEY_INV:
            print([str(f) for f in row])
    except Exception as e:
        print(f"Не удалось вычислить обратную матрицу: {e}")
        KEY_INV = None

    print("="*40)

    while True:
        print("\nМеню:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        op = input("Выберите действие: ").strip()

        if op == '1':
            original = input("Введите открытый текст: ")
            prepared = prepare_text(original)
            print("После обработки (подготовленный текст):", prepared)
            cipher_nums, orig_len = encrypt(prepared, KEY)

            # Вывод результата: список чисел и слитная строка
            print("Шифртекст (числа, без преобразования):", cipher_nums)
            out_str = ''.join(str(x).zfill(OUTPUT_DIGITS) for x in cipher_nums)
            print(f"Шифртекст (строка из {OUTPUT_DIGITS}-значных чисел):", out_str)
            print("Длина исходного текста (после подготовки, символов):", orig_len)

        elif op == '2':
            if KEY_INV is None:
                print("Обратная матрица недоступна, расшифрование невозможно.")
                continue

            inp = input("Введите шифртекст (числа через пробел или слитную строку): ").strip()
            # Определяем формат ввода
            if ' ' in inp:
                nums = list(map(int, inp.split()))
            else:
                # Слитная строка – разбиваем на числа по OUTPUT_DIGITS
                if len(inp) % OUTPUT_DIGITS != 0:
                    print(f"Ошибка: длина строки не кратна {OUTPUT_DIGITS}.")
                    continue
                nums = []
                for i in range(0, len(inp), OUTPUT_DIGITS):
                    part = inp[i:i+OUTPUT_DIGITS]
                    nums.append(int(part))

            try:
                orig_len = int(input("Введите длину исходного текста (после подготовки): "))
            except:
                print("Ошибка: длина должна быть целым числом.")
                continue

            try:
                plain = decrypt(nums, KEY_INV, orig_len)
                print("Расшифрованный текст:", plain)
            except Exception as e:
                print("Ошибка расшифрования:", e)

        elif op == '3':
            break
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()