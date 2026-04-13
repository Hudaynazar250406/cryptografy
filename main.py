#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Общий графический интерфейс криптографических алгоритмов
Лаб. 1–11
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import sys
import math
from collections import OrderedDict

try:
    import numpy as np 
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════════════
#  ПРЕДОБРАБОТКА ТЕКСТА
# ═══════════════════════════════════════════════════════════════════════

_P_ENC = {'.': 'тчк', ',': 'зпт', ' ': 'прб'}
_P_DEC = {v: k for k, v in _P_ENC.items()}


def enc_pre(text: str) -> str:
    text = text.replace('ё', 'е').replace('Ё', 'Е')
    for ch, code in _P_ENC.items():
        text = text.replace(ch, code)
    return text.lower()


def dec_pre(text: str) -> str:
    return text.replace(' ', '').lower()


def post(text: str) -> str:
    for code, ch in _P_DEC.items():
        text = text.replace(code, ch)
    if not text:
        return text
    lst = list(text[0].upper() + text[1:])
    for i in range(len(lst) - 2):
        if lst[i] == '.' and i + 2 < len(lst):
            lst[i + 2] = lst[i + 2].upper()
    return ''.join(lst)


# ═══════════════════════════════════════════════════════════════════════
#  ЛАБ. 1 — Классические шифры замены
# ═══════════════════════════════════════════════════════════════════════

_RU = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
_RL = _RU.lower()
_N  = 32


def atbash(text: str) -> str:
    rev = _RU[::-1]
    out = []
    for ch in text:
        up = ch.upper()
        if up in _RU:
            i = _RU.index(up)
            out.append(rev[i] if ch.isupper() else rev[i].lower())
        else:
            out.append(ch)
    return ''.join(out)


def caesar(text: str, shift: int) -> str:
    s = int(shift) % _N
    out = []
    for ch in text:
        if ch in _RL:
            out.append(_RL[(_RL.index(ch) + s) % _N])
        elif ch in _RU:
            out.append(_RU[(_RU.index(ch) + s) % _N])
        else:
            out.append(ch)
    return ''.join(out)


def _poly_sq():
    sq, rsq = {}, {}
    alpha = _RU + ' '
    for i, ch in enumerate(alpha):
        r, c = divmod(i, 6)
        k = f"{r+1}{c+1}"
        sq[ch] = k
        rsq[k]  = ch
    return sq, rsq


def poly_enc(text: str) -> str:
    sq, _ = _poly_sq()
    return ' '.join(sq.get(c.upper(), c) for c in text)


def poly_dec(text: str) -> str:
    _, rsq = _poly_sq()
    return ''.join(rsq.get(p, p) for p in text.split()).lower()


# ═══════════════════════════════════════════════════════════════════════
#  ЛАБ. 2 — Шифры Виженера
# ═══════════════════════════════════════════════════════════════════════

_RU2  = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
_AMAT = [[_RU2[(j + i) % 32] for j in range(32)] for i in range(32)]


def _ri(ch: str) -> int:
    return _AMAT[0].index(ch)


def _vcheck(text: str, key: str = '') -> str:
    bad = [c for c in text if c not in _RU2]
    if bad:
        return f"Символы не в алфавите: {set(bad)}"
    if key:
        bad2 = [c for c in key if c not in _RU2]
        if bad2:
            return f"Символы ключа не в алфавите: {set(bad2)}"
    return ''


def trithemius_enc(text: str) -> str:
    err = _vcheck(text)
    if err:
        return err
    return ''.join(_AMAT[i % 32][_ri(ch)] for i, ch in enumerate(text))


def trithemius_dec(text: str) -> str:
    err = _vcheck(text)
    if err:
        return err
    return ''.join(_AMAT[0][_AMAT[i % 32].index(ch)] for i, ch in enumerate(text))


def belazo_enc(text: str, key: str) -> str:
    k = key.lower()
    err = _vcheck(text, k)
    if err:
        return err
    return ''.join(_AMAT[_ri(k[i % len(k)])][_ri(ch)] for i, ch in enumerate(text))


def belazo_dec(text: str, key: str) -> str:
    k = key.lower()
    err = _vcheck(text, k)
    if err:
        return err
    return ''.join(_AMAT[0][_AMAT[_ri(k[i % len(k)])].index(ch)] for i, ch in enumerate(text))


def vigenere_enc(text: str, key: str) -> str:
    k = key.lower()
    err = _vcheck(text, k)
    if err:
        return err
    kf = k + text
    return ''.join(_AMAT[_ri(kf[i])][_ri(ch)] for i, ch in enumerate(text))


def vigenere_dec(text: str, key: str) -> str:
    k = key.lower()
    err = _vcheck(text, k)
    if err:
        return err
    kf = list(k)
    result = ''
    for ch in text:
        oc = _AMAT[_AMAT[_ri(kf[len(result)])].index(ch)][0]
        result += oc
        kf.append(oc)
    return result


def vigenere2_enc(text: str, key: str) -> str:
    k = key.lower()
    err = _vcheck(text, k)
    if err:
        return err
    kf = list(k)
    result = ''
    for ch in text:
        cc = _AMAT[_ri(kf[len(result)])][_ri(ch)]
        result += cc
        kf.append(cc)
    return result


def vigenere2_dec(text: str, key: str) -> str:
    k = key.lower()
    err = _vcheck(text, k)
    if err:
        return err
    kf = list(k)
    result = ''
    for cc in text:
        oc = _AMAT[0][_AMAT[_ri(kf[len(result)])].index(cc)]
        result += oc
        kf.append(cc)
    return result


# ═══════════════════════════════════════════════════════════════════════
#  ЛАБ. 3 — Полиграфические шифры
# ═══════════════════════════════════════════════════════════════════════

_PF_BASE = "абвгдежзиклмнопрстуфхцчшщъыэюя"  # 30 символов (без й, ь, ё)


def _gen_pf_table(keyword: str):
    kw = ''.join(OrderedDict.fromkeys(keyword.lower() + _PF_BASE))[:30]
    return [[kw[i * 6 + j] for j in range(6)] for i in range(5)]


def _fidx(table, el: str):
    for i, row in enumerate(table):
        if el in row:
            return i, row.index(el)
    return None, None


def _prep_pf(text: str) -> str:
    text = text.replace('й', 'и').replace('ь', 'ъ').replace('ё', 'е')
    res, i = '', 0
    while i < len(text):
        f = text[i]
        if i + 1 < len(text):
            s = text[i + 1]
            if f == s:
                res += f + 'ф'
                i += 1
            else:
                res += f + s
                i += 2
        else:
            res += f + 'ф'
            i += 1
    return res


def playfair_enc(text: str, key: str) -> str:
    try:
        text = _prep_pf(text.lower())
        table = _gen_pf_table(key)
        result = ''
        for i in range(0, len(text), 2):
            a, b = text[i], text[i + 1]
            r1, c1 = _fidx(table, a)
            r2, c2 = _fidx(table, b)
            if r1 is None or r2 is None:
                continue
            if r1 == r2:
                result += table[r1][(c1 + 1) % 6] + table[r2][(c2 + 1) % 6]
            elif c1 == c2:
                result += table[(r1 + 1) % 5][c1] + table[(r2 + 1) % 5][c2]
            else:
                result += table[r1][c2] + table[r2][c1]
        return ' '.join(result[i:i + 5] for i in range(0, len(result), 5))
    except Exception as e:
        return f"Ошибка: {e}"


def playfair_dec(text: str, key: str) -> str:
    try:
        text = text.replace(' ', '').lower()
        table = _gen_pf_table(key)
        result = ''
        for i in range(0, len(text) - 1, 2):
            a, b = text[i], text[i + 1]
            r1, c1 = _fidx(table, a)
            r2, c2 = _fidx(table, b)
            if r1 is None or r2 is None:
                continue
            if r1 == r2:
                result += table[r1][(c1 - 1) % 6] + table[r2][(c2 - 1) % 6]
            elif c1 == c2:
                result += table[(r1 - 1) % 5][c1] + table[(r2 - 1) % 5][c2]
            else:
                result += table[r1][c2] + table[r2][c1]
        return result
    except Exception as e:
        return f"Ошибка: {e}"


def matrix_enc(text: str, matrix: str) -> str:
    if not HAS_NUMPY:
        return "Ошибка: numpy не установлен. Выполните: pip install numpy"
    alpha = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    try:
        km = np.array(list(map(float, matrix.split()))).reshape(3, 3)
    except Exception as e:
        return f"Неверная матрица: {e}"
    if abs(np.linalg.det(km)) < 1e-9:
        return "Ошибка: определитель матрицы = 0 (матрица необратима)"
    text += 'ф' * ((3 - len(text) % 3) % 3)
    parts = []
    for i in range(0, len(text), 3):
        try:
            v = np.array([[alpha.index(text[i + j]) + 1] for j in range(3)], dtype=float)
        except ValueError as e:
            return f"Символ не в алфавите: {e}"
        r = np.matmul(km, v)
        parts.extend([str(int(round(r[k, 0]))) for k in range(3)])
    return ' '.join(parts)


def matrix_dec(text: str, matrix: str) -> str:
    if not HAS_NUMPY:
        return "Ошибка: numpy не установлен"
    alpha = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
    try:
        km = np.linalg.inv(np.array(list(map(float, matrix.split()))).reshape(3, 3))
    except Exception as e:
        return f"Неверная матрица: {e}"
    try:
        nums = list(map(int, text.strip().split()))
    except Exception:
        return "Ошибка: шифртекст должен содержать числа через пробел"
    result = ''
    for i in range(0, len(nums) - 2, 3):
        v = np.array([[nums[i + k]] for k in range(3)], dtype=float)
        r = np.matmul(km, v)
        for k in range(3):
            idx = int(round(r[k, 0])) - 1
            if 0 <= idx < len(alpha):
                result += alpha[idx]
    return post(result.rstrip('ф'))


# ═══════════════════════════════════════════════════════════════════════
#  ЛАБ. 5 — Шифр-блокнот Шеннона
# ═══════════════════════════════════════════════════════════════════════

_LA5 = list('абвгдежзийклмнопрстуфхцчшщъыьэюя')
_M5  = 32


def _gamma(a: int, c: int, t0: int, n: int):
    t, g = t0, []
    for _ in range(n):
        t = (a * t + c) % _M5
        g.append(t)
    return g


def shannon_enc(text: str, a, c, t0) -> str:
    try:
        a, c, t0 = int(a), int(c), int(t0)
    except Exception:
        return "Ошибка: a, c, T₀ должны быть целыми числами"
    digital = []
    for ch in text:
        if ch not in _LA5:
            return f"Символ '{ch}' не в алфавите. Используйте только русские буквы."
        digital.append(_LA5.index(ch) + 1)
    g = _gamma(a, c, t0, len(digital))
    enc = [((p - 1 + gi) % _M5) + 1 for p, gi in zip(digital, g)]
    return ''.join(_LA5[e - 1] for e in enc)


def shannon_dec(text: str, a, c, t0) -> str:
    try:
        a, c, t0 = int(a), int(c), int(t0)
    except Exception:
        return "Ошибка: a, c, T₀ должны быть целыми числами"
    digital = []
    for ch in text:
        if ch not in _LA5:
            return f"Символ '{ch}' не в алфавите."
        digital.append(_LA5.index(ch) + 1)
    g = _gamma(a, c, t0, len(digital))
    dec = [((e - 1 - gi) % _M5) + 1 for e, gi in zip(digital, g)]
    return post(''.join(_LA5[d - 1] for d in dec))


# ═══════════════════════════════════════════════════════════════════════
#  КАТАЛОГ ШИФРОВ
# ═══════════════════════════════════════════════════════════════════════

CIPHER_CATALOG = [
    {
        "group": "Лаб. 1 — Классические шифры замены",
        "items": [
            {
                "id": "atbash",
                "name": "Атбаш",
                "description": (
                    "Древний шифр обратной замены. Каждая буква алфавита заменяется "
                    "зеркально расположенной: А↔Я, Б↔Э, В↔Ю, Г↔Ь...\n\n"
                    "Шифр является инволюцией: шифрование и расшифрование — одна и та же операция."
                ),
                "type": "Симметричный",
                "category": "Подстановочный (моноалфавитный)",
                "key": "Без ключа (инволюция)",
                "params": [],
                "encrypt": lambda t, **p: atbash(enc_pre(t)),
                "decrypt": lambda t, **p: post(atbash(dec_pre(t))),
            },
            {
                "id": "caesar",
                "name": "Цезарь",
                "description": (
                    "Шифр сдвига Цезаря. Каждая буква сдвигается на K позиций вперёд по алфавиту.\n\n"
                    "Алфавит: 32 русские буквы (без Ё). Ключ: целое число K (K mod 32 ≠ 0).\n\n"
                    "Расшифровка выполняется сдвигом на −K позиций."
                ),
                "type": "Симметричный",
                "category": "Подстановочный (моноалфавитный)",
                "key": "Числовой сдвиг K (K mod 32 ≠ 0)",
                "params": [
                    {"name": "shift", "label": "Сдвиг (K)", "default": "3"},
                ],
                "encrypt": lambda t, shift='3', **p: caesar(enc_pre(t), int(shift)),
                "decrypt": lambda t, shift='3', **p: post(caesar(dec_pre(t), -int(shift))),
            },
            {
                "id": "polybius",
                "name": "Полибий",
                "description": (
                    "Шифр полибийского квадрата. Алфавит (32 буквы + пробел) располагается "
                    "в таблице 6×6. Каждая буква заменяется парой цифр (строка, столбец).\n\n"
                    "Шифртекст: числа через пробел (напр. '11 12 21').\n"
                    "При расшифровании введите эти числа."
                ),
                "type": "Симметричный",
                "category": "Подстановочный",
                "key": "Без ключа",
                "params": [],
                "encrypt": lambda t, **p: poly_enc(enc_pre(t)),
                "decrypt": lambda t, **p: post(poly_dec(t.strip())),
            },
        ],
    },
    {
        "group": "Лаб. 2 — Шифры Виженера",
        "items": [
            {
                "id": "trithemius",
                "name": "Тритемий",
                "description": (
                    "Прогрессивный ключ (без ключевого слова). i-я буква шифруется со "
                    "сдвигом i (mod 32), используя таблицу Виженера.\n\n"
                    "Частный случай шифра Виженера, где ключ — натуральный ряд чисел."
                ),
                "type": "Симметричный",
                "category": "Полиалфавитный подстановочный",
                "key": "Без ключа (прогрессивный сдвиг)",
                "params": [],
                "encrypt": lambda t, **p: trithemius_enc(enc_pre(t)),
                "decrypt": lambda t, **p: post(trithemius_dec(dec_pre(t))),
            },
            {
                "id": "belazo",
                "name": "Белазо (Виженер с ключом)",
                "description": (
                    "Классический шифр Виженера с ключевым словом. Ключ циклически "
                    "повторяется вдоль текста. Каждая буква шифруется со сдвигом, "
                    "определённым соответствующей буквой ключа."
                ),
                "type": "Симметричный",
                "category": "Полиалфавитный подстановочный",
                "key": "Ключевое слово (русские буквы)",
                "params": [{"name": "key", "label": "Ключевое слово", "default": "ключ"}],
                "encrypt": lambda t, key='ключ', **p: belazo_enc(enc_pre(t), key),
                "decrypt": lambda t, key='ключ', **p: post(belazo_dec(dec_pre(t), key)),
            },
            {
                "id": "vigenere",
                "name": "Виженер (автоключ — открытый текст)",
                "description": (
                    "Автоключ Виженера по открытому тексту.\n\n"
                    "Ключ = начальное слово + буквы открытого текста. "
                    "Каждый зашифрованный символ уже не нужен для расширения ключа."
                ),
                "type": "Симметричный",
                "category": "Полиалфавитный подстановочный",
                "key": "Начальный ключ (русские буквы)",
                "params": [{"name": "key", "label": "Начальный ключ", "default": "ключ"}],
                "encrypt": lambda t, key='ключ', **p: vigenere_enc(enc_pre(t), key),
                "decrypt": lambda t, key='ключ', **p: post(vigenere_dec(dec_pre(t), key)),
            },
            {
                "id": "vigenere2",
                "name": "Виженер-2 (автоключ — шифртекст)",
                "description": (
                    "Автоключ Виженера по шифртексту.\n\n"
                    "Ключ = начальное слово + буквы шифртекста. "
                    "Каждый зашифрованный символ расширяет ключ для следующего."
                ),
                "type": "Симметричный",
                "category": "Полиалфавитный подстановочный",
                "key": "Начальный ключ (русские буквы)",
                "params": [{"name": "key", "label": "Начальный ключ", "default": "ключ"}],
                "encrypt": lambda t, key='ключ', **p: vigenere2_enc(enc_pre(t), key),
                "decrypt": lambda t, key='ключ', **p: post(vigenere2_dec(dec_pre(t), key)),
            },
        ],
    },
    {
        "group": "Лаб. 3 — Полиграфические шифры",
        "items": [
            {
                "id": "playfair",
                "name": "Плейфер",
                "description": (
                    "Биграммный шифр замены. Текст разбивается на пары букв, "
                    "которые шифруются по правилам таблицы 5×6, построенной на ключевом слове.\n\n"
                    "Правила:\n"
                    "• Одна строка → сдвиг вправо на 1\n"
                    "• Один столбец → сдвиг вниз на 1\n"
                    "• Прямоугольник → обмен столбцами\n\n"
                    "Й→И, Ь→Ъ, Ё→Е заменяются автоматически."
                ),
                "type": "Симметричный",
                "category": "Полиграфический подстановочный",
                "key": "Ключевое слово",
                "params": [{"name": "key", "label": "Ключевое слово", "default": "ключ"}],
                "encrypt": lambda t, key='ключ', **p: playfair_enc(enc_pre(t), key),
                "decrypt": lambda t, key='ключ', **p: post(playfair_dec(t, key)),
            },
            {
                "id": "matrix",
                "name": "Матричный шифр (Хилла)",
                "description": (
                    "Шифр Хилла. Текст разбивается на тройки букв, преобразуется в числа "
                    "(а=1, б=2, ..., я=32) и умножается на матрицу-ключ 3×3.\n\n"
                    "Шифртекст: числа через пробел (напр. '5 7 3 10 2 8').\n"
                    "При расшифровании введите эти числа.\n\n"
                    "Требует: pip install numpy"
                ),
                "type": "Симметричный",
                "category": "Полиграфический подстановочный",
                "key": "Матрица 3×3 (определитель ≠ 0), 9 чисел через пробел",
                "params": [{"name": "matrix", "label": "Матрица (9 чисел)", "default": "1 0 0 0 1 0 0 0 1"}],
                "encrypt": lambda t, matrix='1 0 0 0 1 0 0 0 1', **p: matrix_enc(enc_pre(t), matrix),
                "decrypt": lambda t, matrix='1 0 0 0 1 0 0 0 1', **p: matrix_dec(t.strip(), matrix),
            },
        ],
    },
    {
        "group": "Лаб. 4 — Шифры перестановки",
        "items": [
            {
                "id": "cardano",
                "name": "Решётка Кардано",
                "mode": "terminal",
                "script": "lab4/lab4.py",
                "description": (
                    "Трафаретный шифр перестановки. Решётка с отверстиями накладывается "
                    "на таблицу и поворачивается 4 раза (0°, 90°, 180°, 270°).\n\n"
                    "Два варианта трафарета:\n"
                    "• 6×10 — для текстов до 60 символов\n"
                    "• 10×10 — для текстов более 60 символов"
                ),
                "type": "Симметричный",
                "category": "Перестановочный (трафаретный)",
                "key": "Без ключа (фиксированный трафарет)",
            },
            {
                "id": "vert_perm",
                "name": "Вертикальная перестановка",
                "mode": "terminal",
                "script": "lab4/lab4.py",
                "description": (
                    "Текст записывается в таблицу построчно. Порядок чтения столбцов "
                    "определяется ключевым словом: позиции букв в алфавите задают "
                    "номера столбцов при считывании."
                ),
                "type": "Симметричный",
                "category": "Перестановочный",
                "key": "Ключевое слово (русские буквы)",
            },
        ],
    },
    {
        "group": "Лаб. 5 — Поточный шифр Шеннона",
        "items": [
            {
                "id": "shannon",
                "name": "Шифр-блокнот Шеннона",
                "description": (
                    "Поточный шифр на основе линейного конгруэнтного генератора (ЛКГ).\n"
                    "Формула гаммы: T(i+1) = (a · T(i) + c) mod 32\n\n"
                    "Условия максимального периода (теорема Халла–Добелла, m=32=2⁵):\n"
                    "• a ≥ 5, нечётное, a ≡ 1 (mod 4)  →  5, 9, 13, 17, 21...\n"
                    "• c нечётное, НОД(c, 32)=1, 0 < c < 32  →  1, 3, 5, 7...\n"
                    "• 0 ≤ T₀ ≤ 31"
                ),
                "type": "Симметричный (поточный)",
                "category": "Поточный шифр (ЛКГ)",
                "key": "Параметры ЛКГ: a, c, T₀",
                "params": [
                    {"name": "a",  "label": "a  (≥5, нечётное, ≡1 mod 4)", "default": "5"},
                    {"name": "c",  "label": "c  (нечётное, 0 < c < 32)",    "default": "1"},
                    {"name": "t0", "label": "T₀  (0 ≤ T₀ ≤ 31)",           "default": "0"},
                ],
                "encrypt": lambda t, a='5', c='1', t0='0', **p: shannon_enc(enc_pre(t), a, c, t0),
                "decrypt": lambda t, a='5', c='1', t0='0', **p: shannon_dec(dec_pre(t), a, c, t0),
            },
        ],
    },
    {
        "group": "Лаб. 6 — A5/1, A5/2 (GSM)",
        "items": [
            {
                "id": "a5_1",
                "name": "A5/1",
                "mode": "terminal",
                "script": "lab6/lab6.py",
                "description": (
                    "Поточный шифр A5/1, применяемый в GSM для защиты голосовых переговоров.\n\n"
                    "Состоит из трёх РСОС (регистров сдвига с линейной обратной связью):\n"
                    "• R1: 19 бит,  обратная связь: биты 13, 16, 17, 18\n"
                    "• R2: 22 бита, обратная связь: биты 20, 21\n"
                    "• R3: 23 бита, обратная связь: биты 7, 20, 21, 22\n\n"
                    "Управление тактированием — по принципу большинства (биты 8, 10, 10).\n"
                    "Загрузка: 64 такта (ключ) + 22 такта (номер кадра) + 100 тактов перемешивания."
                ),
                "type": "Симметричный (поточный)",
                "category": "Поточный шифр (РСОС)",
                "key": "64-битный ключ (двоичная строка 0/1) или 8 русских букв",
            },
            {
                "id": "a5_2",
                "name": "A5/2",
                "mode": "terminal",
                "script": "lab6/lab6_2.py",
                "description": (
                    "Поточный шифр A5/2 — модификация A5/1 с дополнительным управляющим регистром R4.\n\n"
                    "Четыре РСОС:\n"
                    "• R1: 19 бит,  обратная связь: биты 0, 14, 17, 18\n"
                    "• R2: 22 бита, обратная связь: биты 0, 21\n"
                    "• R3: 23 бита, обратная связь: биты 0, 8, 21, 22\n"
                    "• R4: 17 бит (управляющий), обратная связь: биты 0, 12\n\n"
                    "Механизм stop-go: R4 управляет тактированием R1, R2, R3\n"
                    "по мажоритарной функции maj(R4[3], R4[7], R4[10]).\n\n"
                    "Выход: R1[18] ⊕ R2[21] ⊕ R3[22] ⊕ maj(R1) ⊕ maj(R2) ⊕ maj(R3)\n\n"
                    "Загрузка: 64 такта (ключ) + 22 такта (номер кадра),\n"
                    "затем R4[3]=R4[7]=R4[10]=1 и 99 тактов перемешивания без вывода.\n\n"
                    "Ключ: 64-битная строка (0/1) или 8 русских букв → 64 бита."
                ),
                "type": "Симметричный (поточный)",
                "category": "Поточный шифр (РСОС, stop-go)",
                "key": "64-битный ключ + 22-битный номер кадра",
            },
        ],
    },
    {
        "group": "Лаб. 7 — Блочные шифры",
        "items": [
            {
                "id": "magma",
                "name": "МАГМА (ГОСТ Р 34.12-2015)",
                "mode": "terminal",
                "script": "lab7/lab7.py",
                "description": (
                    "Блочный симметричный шифр «Магма» (ранее ГОСТ 28147-89).\n\n"
                    "Параметры алгоритма:\n"
                    "• Размер блока: 64 бита (8 байт)\n"
                    "• Длина ключа:  256 бит (64 hex-символа)\n"
                    "• Число раундов: 32 (32 подключа)\n"
                    "• Структура: сеть Фейстеля\n"
                    "• Нелинейность: 8 таблиц подстановки pi_0…pi_7 (4→4 бита)\n\n"
                    "Расписание ключей: K1..K24 = k0..k7 ×3; K25..K32 = k7..k0."
                ),
                "type": "Симметричный (блочный)",
                "category": "Блочный шифр (сеть Фейстеля)",
                "key": "256-битный ключ (64 hex-символа)",
            },
            {
                "id": "gost_magma_simple",
                "name": "ГОСТ Магма (простая замена)",
                "mode": "terminal",
                "script": "lab7/gostmagma1prostzamena(magma).py",
                "description": (
                    "ГОСТ 28147-89 в режиме простой замены.\n\n"
                    "Параметры алгоритма:\n"
                    "• Размер блока: 64 бита (8 байт)\n"
                    "• Длина ключа:  256 бит (64 hex-символа)\n"
                    "• Число раундов: 32\n"
                    "• Режим: ECB (простая замена — каждый блок шифруется независимо)\n\n"
                    "Отличие от основной Магмы: нет сцепления блоков."
                ),
                "type": "Симметричный (блочный)",
                "category": "Блочный шифр (сеть Фейстеля, ECB)",
                "key": "256-битный ключ (64 hex-символа)",
            },
            {
                "id": "kuznechik",
                "name": "Кузнечик (ГОСТ Р 34.12-2015)",
                "mode": "terminal",
                "script": "lab7/kuznech.py",
                "description": (
                    "Блочный шифр «Кузнечик» — современный российский стандарт.\n\n"
                    "Параметры алгоритма:\n"
                    "• Размер блока: 128 бит (16 байт)\n"
                    "• Длина ключа:  256 бит (32 байта)\n"
                    "• Число раундов: 10\n"
                    "• Структура: SP-сеть (подстановка + перестановка)\n"
                    "• Нелинейный слой: таблица π (256 элементов)\n"
                    "• Линейный слой: умножение на матрицу в GF(2⁸)\n\n"
                    "Принят как стандарт вместе с Магмой в ГОСТ Р 34.12-2015."
                ),
                "type": "Симметричный (блочный)",
                "category": "Блочный шифр (SP-сеть)",
                "key": "256-битный ключ (64 hex-символа)",
            },
            {
                "id": "aes",
                "name": "AES (Advanced Encryption Standard)",
                "mode": "terminal",
                "script": "lab7/AES.py",
                "description": (
                    "Международный стандарт блочного шифрования AES (Rijndael).\n\n"
                    "Параметры алгоритма:\n"
                    "• Размер блока: 128 бит (16 байт)\n"
                    "• Длина ключа:  128 / 192 / 256 бит\n"
                    "• Число раундов: 10 / 12 / 14 (зависит от длины ключа)\n"
                    "• Структура: SP-сеть (SubBytes, ShiftRows, MixColumns, AddRoundKey)\n\n"
                    "Принят как стандарт NIST в 2001 году. Используется повсеместно."
                ),
                "type": "Симметричный (блочный)",
                "category": "Блочный шифр (SP-сеть)",
                "key": "128/192/256-битный ключ",
            },
        ],
    },
    {
        "group": "Лаб. 8 — Асимметричные шифры",
        "items": [
            {
                "id": "rsa_enc",
                "name": "RSA (шифрование)",
                "mode": "terminal",
                "script": "lab8/lab8.py",
                "description": (
                    "Асимметричный алгоритм RSA.\n\n"
                    "Генерация ключей:\n"
                    "  n = P·Q,  φ(n) = (P−1)(Q−1)\n"
                    "  Выбор E: НОД(E, φ) = 1\n"
                    "  D = E⁻¹ mod φ  (расширенный алгоритм Евклида)\n\n"
                    "Шифрование: c = mᴱ mod n\n"
                    "Расшифрование: m = cᴰ mod n\n\n"
                    "Безопасность: задача факторизации больших чисел."
                ),
                "type": "Асимметричный",
                "category": "Шифрование с открытым ключом",
                "key": "P, Q (простые числа); E — открытая экспонента",
            },
            {
                "id": "elgamal_enc",
                "name": "ElGamal (шифрование)",
                "mode": "terminal",
                "script": "lab8/lab8.py",
                "description": (
                    "Асимметричный алгоритм Эль-Гамаля.\n\n"
                    "Ключи: y = gˣ mod p (открытый), x (закрытый)\n"
                    "Шифрование символа m: a = gᵏ mod p,  b = yᵏ·m mod p\n"
                    "Расшифрование: m = b · (aˣ)⁻¹ mod p\n\n"
                    "k — случайный для каждого символа.\n"
                    "Безопасность: задача дискретного логарифма."
                ),
                "type": "Асимметричный",
                "category": "Шифрование с открытым ключом",
                "key": "p (простое), g, x (секретный ключ); k — случайный на каждый символ",
            },
            {
                "id": "ecc_enc",
                "name": "ECC (эллиптические кривые)",
                "mode": "terminal",
                "script": "lab8/lab8.py",
                "description": (
                    "Шифрование на эллиптических кривых.\n\n"
                    "Кривая: y² = x³ + ax + b  (mod p)\n"
                    "Открытый ключ получателя: D_b = C_b · G\n"
                    "Шифрование: R = k·G,  P_pt = k·D_b,  e = m · P_pt.x  mod p\n"
                    "Расшифрование: Q = C_b·R,  m = e · Q.x⁻¹  mod p"
                ),
                "type": "Асимметричный",
                "category": "Шифрование на эллиптических кривых",
                "key": "a, b, p — параметры кривой; G — базовая точка; C_b, q_m; k, m",
            },
            {
                "id": "rsa_sign_8",
                "name": "RSA — цифровая подпись",
                "mode": "terminal",
                "script": "lab8/lab8.py",
                "description": (
                    "Цифровая подпись RSA.\n\n"
                    "Подписание: S = h(m)ᴰ mod n\n"
                    "Проверка:   h(m) == Sᴱ mod n\n\n"
                    "Хеш-функция: h(text) = (Σ индексов букв  mod (n−1)) + 1"
                ),
                "type": "Асимметричный",
                "category": "Цифровая подпись",
                "key": "P, Q, E; открытый ключ (E, N), закрытый (D, N)",
            },
            {
                "id": "elgamal_sign_8",
                "name": "ElGamal — цифровая подпись",
                "mode": "terminal",
                "script": "lab8/lab8.py",
                "description": (
                    "Цифровая подпись Эль-Гамаля.\n\n"
                    "Ключи: Y = Gˣ mod P (открытый), X (закрытый)\n"
                    "Подписание: R = Gᴷ mod P,  S = K⁻¹(m − X·R)  mod (P−1)\n"
                    "Проверка: Yᴿ · Rˢ mod P  ==  Gᵐ mod P"
                ),
                "type": "Асимметричный",
                "category": "Цифровая подпись",
                "key": "P (простое), G, X (секретный), K — случайный (НОД(K,P−1)=1)",
            },
        ],
    },
    {
        "group": "Лаб. 9 — Цифровые подписи",
        "items": [
            {
                "id": "rsa_sign_9",
                "name": "RSA (подпись, квадратичный хеш)",
                "mode": "terminal",
                "script": "lab9/lab9.py",
                "description": (
                    "Цифровая подпись RSA с квадратичной хеш-функцией.\n\n"
                    "Хеш: hᵢ = (h_{i−1} + индекс_буквы + 1)²  mod n\n\n"
                    "Подписание: S = hᴰ mod n\n"
                    "Проверка:   h == Sᴱ mod n"
                ),
                "type": "Асимметричный",
                "category": "Цифровая подпись",
                "key": "P, Q (простые числа)",
            },
            {
                "id": "elgamal_sign_9",
                "name": "ElGamal (подпись, квадратичный хеш)",
                "mode": "terminal",
                "script": "lab9/lab9.py",
                "description": (
                    "Цифровая подпись Эль-Гамаля с квадратичной хеш-функцией.\n\n"
                    "Параметры: P (простое), G, X (секрет), K (случайный).\n"
                    "Подпись: пара (A, B).\n"
                    "Проверка: Yᴬ · Aᴮ mod P  ==  Gᵐ mod P"
                ),
                "type": "Асимметричный",
                "category": "Цифровая подпись",
                "key": "P (простое), G, X (секрет)",
            },
        ],
    },
    {
        "group": "Лаб. 10 — ГОСТ ЭЦП",
        "items": [
            {
                "id": "gost94",
                "name": "ГОСТ Р 34.10-94",
                "mode": "terminal",
                "script": "lab10/lab10.py",
                "description": (
                    "Стандарт ЭЦП на основе задачи дискретного логарифма.\n\n"
                    "Параметры: P (простое), Q (простой делитель P−1), a (генератор)\n"
                    "Подписание: r = (aᵏ mod P) mod Q,  s = (x·r + k·m) mod Q\n"
                    "Проверка:   u = (a^z1 · y^z2 mod P) mod Q,  u == r\n\n"
                    "Параметр a вычисляется автоматически."
                ),
                "type": "Асимметричный",
                "category": "Цифровая подпись (ГОСТ)",
                "key": "P, Q (Q|P−1), x (закрытый ключ)",
            },
            {
                "id": "gost2012",
                "name": "ГОСТ Р 34.10-2012",
                "mode": "terminal",
                "script": "lab10/lab10.py",
                "description": (
                    "Стандарт ЭЦП на эллиптических кривых (2012).\n\n"
                    "Кривая: y² = x³ + ax + b  (mod p)\n"
                    "Базовая точка G, порядок q = |G|\n"
                    "Подписание: C = k·G,  r = C.x mod q,  s = (k·m + r·x_A) mod q\n"
                    "Проверка:   R = u1·G + u2·Y_A,  R.x mod q  ==  r"
                ),
                "type": "Асимметричный",
                "category": "Цифровая подпись (ГОСТ, ЭК)",
                "key": "a, b, p — кривая; G — базовая точка; x_A — закрытый ключ",
            },
        ],
    },
    {
        "group": "Лаб. 11 — Протокол Диффи-Хеллмана",
        "items": [
            {
                "id": "dh",
                "name": "Диффи-Хеллман",
                "mode": "terminal",
                "script": "lab11/lab11.py",
                "description": (
                    "Протокол обмена ключами по открытому каналу.\n\n"
                    "Параметры: n (простое > 2), a (основание, 1 < a < n)\n\n"
                    "Сторона A: генерирует K_A (секрет), публикует Y_A = aᴷᴬ mod n\n"
                    "Сторона B: генерирует K_B (секрет), публикует Y_B = aᴷᴮ mod n\n\n"
                    "Общий ключ: K = Y_B^K_A mod n  =  Y_A^K_B mod n\n\n"
                    "Безопасность: задача дискретного логарифма.\n"
                    "Программа автоматически генерирует секретные ключи сторон."
                ),
                "type": "Асимметричный (обмен ключами)",
                "category": "Криптографический протокол",
                "key": "n (простое > 2), a (основание, 1 < a < n)",
            },
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════
#  ЦВЕТА И СТИЛИ
# ═══════════════════════════════════════════════════════════════════════

C = {
    'bg':       '#f4f4f8',
    'sidebar':  '#1e1e2e',
    'header':   '#313244',
    'accent':   '#89b4fa',
    'sel':      '#45475a',
    'fg_dark':  '#cdd6f4',
    'fg_light': '#1e1e2e',
    'enc':      '#a6e3a1',
    'dec':      '#89b4fa',
    'term_bg':  '#1e1e2e',
    'term_fg':  '#cdd6f4',
    'card':     '#ffffff',
    'border':   '#d0d0e8',
}


# ═══════════════════════════════════════════════════════════════════════
#  ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════

class CryptoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Криптографический интерфейс  —  Лаб. 1–11")
        self.root.geometry("1260x780")
        self.root.minsize(950, 620)
        self.root.configure(bg=C['bg'])

        self.current_cipher = None
        self.proc = None
        self.param_vars: dict = {}
        self._cipher_map: dict = {}

        self._setup_styles()
        self._build_ui()

    # ──────────────────────────────────────────────────────────────────
    # Стили
    # ──────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')

        s.configure('Treeview',
                    background=C['sidebar'],
                    foreground='#bac2de',
                    fieldbackground=C['sidebar'],
                    rowheight=24,
                    font=('Segoe UI', 9),
                    borderwidth=0)
        s.configure('Treeview.Heading',
                    background=C['header'],
                    foreground='#cdd6f4',
                    font=('Segoe UI', 9, 'bold'))
        s.map('Treeview',
              background=[('selected', C['sel'])],
              foreground=[('selected', C['accent'])])

        s.configure('TNotebook', background=C['bg'], borderwidth=0)
        s.configure('TNotebook.Tab',
                    background='#e8e8f4',
                    foreground='#444466',
                    font=('Segoe UI', 9),
                    padding=(10, 4))
        s.map('TNotebook.Tab',
              background=[('selected', C['card'])],
              foreground=[('selected', '#1a1a3e')])

        s.configure('TLabelframe',
                    background=C['bg'],
                    bordercolor=C['border'])
        s.configure('TLabelframe.Label',
                    background=C['bg'],
                    foreground='#555577',
                    font=('Segoe UI', 9))

        for name, bg in [('Enc.TButton', '#40a02b'),
                          ('Dec.TButton', '#1e66f5'),
                          ('Act.TButton', '#df8e1d')]:
            s.configure(name, background=bg, foreground='white',
                        font=('Segoe UI', 9, 'bold'), padding=(10, 5))

    # ──────────────────────────────────────────────────────────────────
    # Построение интерфейса
    # ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Шапка
        hdr = tk.Frame(self.root, bg=C['header'], height=46)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Криптографический интерфейс",
                 bg=C['header'], fg='#cdd6f4',
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, pady=8)
        tk.Label(hdr, text="Лаб. 1–11  |  Выберите шифр  ",
                 bg=C['header'], fg='#6c7086',
                 font=('Segoe UI', 8)).pack(side=tk.RIGHT, pady=8)

        # Тело
        body = tk.Frame(self.root, bg=C['bg'])
        body.pack(fill=tk.BOTH, expand=True)

        # Левая панель
        left = tk.Frame(body, bg=C['sidebar'], width=265)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        self._build_sidebar(left)

        # Разделитель
        tk.Frame(body, bg='#313244', width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Правая панель
        right = tk.Frame(body, bg=C['bg'])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_right(right)

        # Статусная строка
        self.status_var = tk.StringVar(value="Выберите шифр из списка слева")
        tk.Label(self.root, textvariable=self.status_var,
                 bg='#e0e0ec', fg='#555577',
                 font=('Segoe UI', 8), anchor='w', padx=8
                 ).pack(fill=tk.X, side=tk.BOTTOM)

    def _build_sidebar(self, parent):
        tk.Label(parent, text=" Шифры  (Лаб. 1–11)",
                 bg=C['header'], fg='#bac2de',
                 font=('Segoe UI', 9, 'bold'),
                 anchor='w').pack(fill=tk.X)

        frm = tk.Frame(parent, bg=C['sidebar'])
        frm.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(frm, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(frm, show='tree', selectmode='browse',
                                  yscrollcommand=vsb.set)
        vsb.config(command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.column('#0', width=248)

        for group in CIPHER_CATALOG:
            gid = self.tree.insert('', tk.END,
                                    text=f"  {group['group']}",
                                    open=True, tags=('grp',))
            for cipher in group['items']:
                iid = self.tree.insert(gid, tk.END,
                                        text=f"    {cipher['name']}",
                                        tags=('cip',))
                self._cipher_map[iid] = cipher

        self.tree.tag_configure('grp', background='#313244', foreground='#a6adc8')
        self.tree.tag_configure('cip', background=C['sidebar'], foreground='#bac2de')
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _build_right(self, parent):
        # Заголовок
        self.title_var = tk.StringVar(value="Выберите шифр из списка слева")
        tk.Label(parent, textvariable=self.title_var,
                 bg=C['bg'], fg='#1a1a3e',
                 font=('Segoe UI', 14, 'bold'),
                 anchor='w').pack(fill=tk.X, padx=15, pady=(12, 2))

        # Notebook
        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Вкладка 1: Характеристики
        info_tab = tk.Frame(self.nb, bg=C['card'])
        self.nb.add(info_tab, text='  Характеристики  ')
        self._build_info_tab(info_tab)

        # Вкладка 2: Шифрование
        op_tab = tk.Frame(self.nb, bg=C['bg'])
        self.nb.add(op_tab, text='  Шифрование / Расшифрование  ')
        self._build_op_tab(op_tab)

    # ── Вкладка характеристик ─────────────────────────────────────────

    def _build_info_tab(self, parent):
        pad = tk.Frame(parent, bg=C['card'])
        pad.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Таблица свойств
        tbl = tk.Frame(pad, bg=C['card'])
        tbl.pack(fill=tk.X)

        self._props: dict = {}
        rows = [
            ('name',     'Шифр:'),
            ('type',     'Тип:'),
            ('category', 'Категория:'),
            ('key',      'Ключ:'),
        ]
        for i, (key, label) in enumerate(rows):
            tk.Label(tbl, text=label, bg=C['card'], fg='#888899',
                     font=('Segoe UI', 9), anchor='w', width=11
                     ).grid(row=i, column=0, sticky='w', pady=3)
            lbl = tk.Label(tbl, text='—', bg=C['card'], fg='#1a1a3e',
                            font=('Segoe UI', 9, 'bold'),
                            anchor='w', wraplength=700, justify='left')
            lbl.grid(row=i, column=1, sticky='w', padx=6, pady=3)
            self._props[key] = lbl

        # Разделитель
        tk.Frame(pad, bg=C['border'], height=1).pack(fill=tk.X, pady=8)

        # Описание
        tk.Label(pad, text='Описание:', bg=C['card'], fg='#888899',
                 font=('Segoe UI', 9), anchor='w').pack(fill=tk.X)

        self.desc_txt = scrolledtext.ScrolledText(
            pad, height=10, wrap=tk.WORD,
            font=('Segoe UI', 10), bg='#fafafa', fg='#222244',
            relief=tk.FLAT, bd=1, state='disabled')
        self.desc_txt.pack(fill=tk.BOTH, expand=True, pady=4)

    # ── Вкладка операций ──────────────────────────────────────────────

    def _build_op_tab(self, parent):
        self._op_parent = parent

        # Заглушка (до выбора шифра)
        self._placeholder = tk.Label(
            parent, text="Выберите шифр из списка слева",
            bg=C['bg'], fg='#888899', font=('Segoe UI', 12))
        self._placeholder.pack(expand=True)

        # Фрейм для форм-режима
        self.form_frame = tk.Frame(parent, bg=C['bg'])
        self._build_form_widgets(self.form_frame)

        # Фрейм для терминал-режима
        self.term_frame = tk.Frame(parent, bg=C['bg'])
        self._build_term_widgets(self.term_frame)

    def _build_form_widgets(self, parent):
        # Параметры
        self.params_lf = ttk.LabelFrame(parent, text=' Параметры шифра ')
        self.params_lf.pack(fill=tk.X, padx=10, pady=(8, 4))
        self.params_inner = tk.Frame(self.params_lf, bg=C['bg'])
        self.params_inner.pack(fill=tk.X, padx=6, pady=4)

        # Вход
        tk.Label(parent, text='Входной текст:', bg=C['bg'], fg='#333355',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=10, pady=(4, 0))
        self.input_text = scrolledtext.ScrolledText(
            parent, height=5, font=('Segoe UI', 10),
            bg='white', fg='#1a1a3e', wrap=tk.WORD, relief=tk.FLAT, bd=1)
        self.input_text.pack(fill=tk.X, padx=10, pady=(2, 4))

        # Ctrl+A в поле ввода
        def _select_all_in(event=None):
            self.input_text.tag_add(tk.SEL, '1.0', tk.END)
            return 'break'
        self.input_text.bind('<Control-a>', _select_all_in)
        self.input_text.bind('<Control-A>', _select_all_in)

        # Кнопки
        btn_f = tk.Frame(parent, bg=C['bg'])
        btn_f.pack(pady=4)
        ttk.Button(btn_f, text='Зашифровать', style='Enc.TButton',
                   command=self._do_encrypt).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_f, text='Расшифровать', style='Dec.TButton',
                   command=self._do_decrypt).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_f, text='Очистить',
                   command=self._clear_form).pack(side=tk.LEFT, padx=6)

        # Выход
        tk.Label(parent, text='Результат:', bg=C['bg'], fg='#333355',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=10, pady=(4, 0))
        self.output_text = scrolledtext.ScrolledText(
            parent, height=5, font=('Segoe UI', 10),
            bg='#f0f0f8', fg='#1a1a3e', wrap=tk.WORD,
            relief=tk.FLAT, bd=1, state='disabled')
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 2))

        # Разрешаем Ctrl+C и Ctrl+A в поле результата (state=disabled блокирует их)
        def _copy_sel(event=None):
            try:
                sel = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(sel)
            except tk.TclError:
                # Нет выделения — копируем всё
                txt = self.output_text.get('1.0', tk.END).strip()
                if txt:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(txt)
            return 'break'

        def _select_all_out(event=None):
            self.output_text.config(state='normal')
            self.output_text.tag_add(tk.SEL, '1.0', tk.END)
            self.output_text.config(state='disabled')
            return 'break'

        self.output_text.bind('<Control-c>', _copy_sel)
        self.output_text.bind('<Control-a>', _select_all_out)
        self.output_text.bind('<Control-A>', _select_all_out)

        copy_f = tk.Frame(parent, bg=C['bg'])
        copy_f.pack(padx=10, pady=3, anchor='e')
        ttk.Button(copy_f, text='Копировать результат',
                   command=self._copy_result).pack()

    def _build_term_widgets(self, parent):
        tk.Label(parent,
                 text="Интерактивный режим — программа запускается в встроенном терминале",
                 bg=C['bg'], fg='#666688',
                 font=('Segoe UI', 9, 'italic')).pack(anchor='w', padx=10, pady=(6, 2))

        ctrl = tk.Frame(parent, bg=C['bg'])
        ctrl.pack(fill=tk.X, padx=10, pady=2)

        ttk.Button(ctrl, text='▶  Запустить', style='Enc.TButton',
                   command=self._start_terminal).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(ctrl, text='■  Остановить',
                   command=self._stop_terminal).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text='Очистить',
                   command=self._clear_terminal).pack(side=tk.LEFT, padx=4)

        self.proc_lbl = tk.Label(ctrl, text='● Не запущен',
                                  bg=C['bg'], fg='#e06c75',
                                  font=('Segoe UI', 8))
        self.proc_lbl.pack(side=tk.RIGHT, padx=8)

        self.term_out = scrolledtext.ScrolledText(
            parent, height=17,
            font=('Consolas', 10),
            bg=C['term_bg'], fg=C['term_fg'],
            insertbackground='white', relief=tk.FLAT, state='disabled')
        self.term_out.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 2))

        # Ctrl+C и Ctrl+A в терминале
        def _term_copy(event=None):
            try:
                sel = self.term_out.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(sel)
            except tk.TclError:
                txt = self.term_out.get('1.0', tk.END).strip()
                if txt:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(txt)
            return 'break'

        def _term_select_all(event=None):
            self.term_out.config(state='normal')
            self.term_out.tag_add(tk.SEL, '1.0', tk.END)
            self.term_out.config(state='disabled')
            return 'break'

        self.term_out.bind('<Control-c>', _term_copy)
        self.term_out.bind('<Control-a>', _term_select_all)
        self.term_out.bind('<Control-A>', _term_select_all)

        inp_f = tk.Frame(parent, bg=C['bg'])
        inp_f.pack(fill=tk.X, padx=10, pady=(2, 8))

        tk.Label(inp_f, text='>', bg=C['bg'], fg='#888888',
                 font=('Consolas', 10)).pack(side=tk.LEFT)
        self.term_in = tk.Entry(inp_f, font=('Consolas', 10),
                                 bg='#2a2a3e', fg='#cdd6f4',
                                 insertbackground='white',
                                 relief=tk.FLAT, bd=1)
        self.term_in.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 4))
        self.term_in.bind('<Return>', self._send_input)

        ttk.Button(inp_f, text='Отправить',
                   command=self._send_input).pack(side=tk.LEFT)

    # ──────────────────────────────────────────────────────────────────
    # Логика выбора шифра
    # ──────────────────────────────────────────────────────────────────

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cipher = self._cipher_map.get(sel[0])
        if not cipher:
            return  # клик по группе

        self.current_cipher = cipher
        self.title_var.set(cipher['name'])
        self._update_info(cipher)
        self._show_op_panel(cipher)
        self.status_var.set(f"Выбран шифр: {cipher['name']}")

    def _update_info(self, c):
        self._props['name'].config(text=c['name'])
        self._props['type'].config(text=c.get('type', '—'))
        self._props['category'].config(text=c.get('category', '—'))
        self._props['key'].config(text=c.get('key', '—'))

        self.desc_txt.config(state='normal')
        self.desc_txt.delete('1.0', tk.END)
        desc = c.get('description', '')
        if 'notes' in c:
            desc += f"\n\nПримечания:\n{c['notes']}"
        self.desc_txt.insert('1.0', desc)
        self.desc_txt.config(state='disabled')

    def _show_op_panel(self, cipher):
        self._stop_terminal()
        self._placeholder.pack_forget()
        mode = cipher.get('mode', 'form')
        if mode == 'terminal':
            self.form_frame.pack_forget()
            self.term_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.term_frame.pack_forget()
            self.form_frame.pack(fill=tk.BOTH, expand=True)
            self._rebuild_params(cipher)

    def _rebuild_params(self, cipher):
        for w in self.params_inner.winfo_children():
            w.destroy()
        self.param_vars = {}
        params = cipher.get('params', [])
        if not params:
            tk.Label(self.params_inner, text='Ключ не требуется',
                     bg=C['bg'], fg='#888899',
                     font=('Segoe UI', 9, 'italic')).pack(anchor='w')
            return
        for p in params:
            row = tk.Frame(self.params_inner, bg=C['bg'])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=p['label'] + ':', bg=C['bg'], fg='#333355',
                     font=('Segoe UI', 9), width=28, anchor='w').pack(side=tk.LEFT)
            var = tk.StringVar(value=str(p.get('default', '')))
            self.param_vars[p['name']] = var
            tk.Entry(row, textvariable=var, font=('Segoe UI', 10),
                     bg='white', fg='#1a1a3e', relief=tk.FLAT, bd=1,
                     width=35).pack(side=tk.LEFT, padx=4)

    # ──────────────────────────────────────────────────────────────────
    # Форм-режим
    # ──────────────────────────────────────────────────────────────────

    def _do_encrypt(self):
        self._run_cipher('encrypt', 'Зашифровано')

    def _do_decrypt(self):
        self._run_cipher('decrypt', 'Расшифровано')

    def _run_cipher(self, op: str, label: str):
        if not self.current_cipher:
            return
        text = self.input_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Введите текст")
            return
        params = {k: v.get() for k, v in self.param_vars.items()}
        try:
            result = self.current_cipher[op](text, **params)
        except Exception as e:
            result = f"Ошибка: {e}"
        self._set_output(str(result))
        self.status_var.set(label)

    def _set_output(self, text: str):
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', text)
        self.output_text.config(state='disabled')

    def _clear_form(self):
        self.input_text.delete('1.0', tk.END)
        self._set_output('')

    def _copy_result(self):
        result = self.output_text.get('1.0', tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_var.set("Результат скопирован в буфер обмена")

    # ──────────────────────────────────────────────────────────────────
    # Терминал-режим
    # ──────────────────────────────────────────────────────────────────

    def _start_terminal(self):
        self._stop_terminal()
        if not self.current_cipher or 'script' not in self.current_cipher:
            return
        script = os.path.join(BASE_DIR, self.current_cipher['script'])
        if not os.path.exists(script):
            self._twrite(f"[Ошибка] Файл не найден: {script}\n")
            return

        self._twrite(f"{'─'*52}\n▶  {self.current_cipher['name']}\n{'─'*52}\n")

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'

        try:
            self.proc = subprocess.Popen(
                [sys.executable, '-u', script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                env=env,
                cwd=os.path.dirname(script),
            )
        except Exception as e:
            self._twrite(f"[Ошибка запуска] {e}\n")
            return

        self.proc_lbl.config(text='● Выполняется', fg='#a6e3a1')
        threading.Thread(target=self._read_proc, daemon=True).start()

    def _read_proc(self):
        buf = ''
        while self.proc and self.proc.poll() is None:
            try:
                ch = self.proc.stdout.read(1)
                if ch:
                    buf += ch
                    self.root.after(0, self._twrite, ch)
                    if ch == '\n':
                        buf = ''
            except Exception:
                break
        if buf:
            self.root.after(0, self._twrite, '')
        self.root.after(0, self._proc_done)

    def _proc_done(self):
        self._twrite('\n■  Процесс завершён\n' + '─'*52 + '\n')
        self.proc_lbl.config(text='● Завершён', fg='#6c7086')
        self.proc = None

    def _stop_terminal(self):
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None
        if hasattr(self, 'proc_lbl'):
            self.proc_lbl.config(text='● Не запущен', fg='#e06c75')

    def _send_input(self, _event=None):
        text = self.term_in.get()
        self.term_in.delete(0, tk.END)
        if not self.proc or self.proc.poll() is not None:
            self._twrite('[Процесс не запущен. Нажмите "Запустить"]\n')
            return
        self._twrite(text + '\n')
        try:
            self.proc.stdin.write(text + '\n')
            self.proc.stdin.flush()
        except Exception:
            self._twrite('[Ошибка отправки ввода]\n')

    def _clear_terminal(self):
        self.term_out.config(state='normal')
        self.term_out.delete('1.0', tk.END)
        self.term_out.config(state='disabled')

    def _twrite(self, text: str):
        self.term_out.config(state='normal')
        self.term_out.insert(tk.END, text)
        self.term_out.see(tk.END)
        self.term_out.config(state='disabled')


# ═══════════════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    root = tk.Tk()
    try:
        root.iconbitmap('')
    except Exception:
        pass
    CryptoApp(root)
    root.mainloop()
