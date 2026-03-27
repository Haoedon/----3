#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Лабораторная работа: шифры блочной замены
- Матричный шифр (ключ – квадратная матрица 3×3 и более)
- Шифр Плэйфера с прямоугольной таблицей (например, 5×6 для русского алфавита без ЁЙЪ)

Для ключа в шифре Плэйфера выполняется проверка на повторы: выводится список уникальных символов.
"""

import math
from fractions import Fraction

# ------------------------------------------------------------
#                   Матричный шифр
# ------------------------------------------------------------

def input_matrix():
    """Ввод квадратной матрицы с проверкой невырожденности."""
    n = int(input("Введите размер матрицы (n, не меньше 3): "))
    if n < 3:
        raise ValueError("Размер матрицы должен быть не меньше 3")
    print("Введите строки матрицы, каждая строка – целые числа через пробел:")
    matrix = []
    for i in range(n):
        row = list(map(int, input().split()))
        if len(row) != n:
            raise ValueError(f"Строка должна содержать {n} чисел")
        matrix.append(row)
    # Проверка определителя (не должен быть равен 0)
    det = determinant(matrix)
    if det == 0:
        raise ValueError("Матрица вырождена, определитель равен 0. Ключ непригоден.")
    return matrix


def determinant(matrix):
    """Вычисление определителя квадратной матрицы (метод Гаусса, точные дроби)."""
    n = len(matrix)
    a = [row[:] for row in matrix]
    det = Fraction(1)
    for i in range(n):
        pivot = i
        while pivot < n and a[pivot][i] == 0:
            pivot += 1
        if pivot == n:
            return Fraction(0)
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            det *= -1
        det *= a[i][i]
        for j in range(i + 1, n):
            factor = Fraction(a[j][i], a[i][i])
            for k in range(i, n):
                a[j][k] -= factor * a[i][k]
    return det


def inverse_matrix(matrix):
    """Вычисление обратной матрицы методом Гаусса‑Жордана (точные дроби)."""
    n = len(matrix)
    aug = []
    for i in range(n):
        row = [Fraction(x) for x in matrix[i]]
        ident = [Fraction(1) if j == i else Fraction(0) for j in range(n)]
        aug.append(row + ident)

    for i in range(n):
        pivot = i
        while pivot < n and aug[pivot][i] == 0:
            pivot += 1
        if pivot == n:
            raise ValueError("Матрица вырождена")
        if pivot != i:
            aug[i], aug[pivot] = aug[pivot], aug[i]

        div = aug[i][i]
        for j in range(2 * n):
            aug[i][j] /= div

        for k in range(n):
            if k != i:
                factor = aug[k][i]
                if factor != 0:
                    for j in range(2 * n):
                        aug[k][j] -= factor * aug[i][j]

    inv = [row[n:] for row in aug]
    return inv


def multiply_matrix_vector(A, v):
    """Умножение матрицы на вектор-столбец."""
    n = len(A)
    res = [Fraction(0) for _ in range(n)]
    for i in range(n):
        for j in range(n):
            res[i] += A[i][j] * v[j]
    return res


def encrypt_matrix(text, matrix, alphabet):
    """
    Шифрование текста матричным шифром.
    Возвращает список целых чисел.
    """
    n = len(matrix)
    indices = [alphabet.index(c) + 1 for c in text]
    pad_len = (n - len(indices) % n) % n
    indices += [1] * pad_len  # дополняем буквой 'А' (индекс 1)

    blocks = [indices[i:i + n] for i in range(0, len(indices), n)]
    cipher = []
    for block in blocks:
        vec = [Fraction(x) for x in block]
        res = multiply_matrix_vector(matrix, vec)
        for r in res:
            if r.denominator != 1:
                raise ValueError("Результат не целый – возможно, матрица не подходит")
            cipher.append(int(r))
    return cipher


def decrypt_matrix(cipher, matrix, alphabet):
    """
    Расшифрование последовательности чисел матричным шифром.
    Возвращает строку (может содержать дополненные символы в конце).
    """
    n = len(matrix)
    inv = inverse_matrix(matrix)
    blocks = [cipher[i:i + n] for i in range(0, len(cipher), n)]
    plain_indices = []
    for block in blocks:
        vec = [Fraction(x) for x in block]
        res = multiply_matrix_vector(inv, vec)
        for r in res:
            if r.denominator != 1:
                raise ValueError("Ошибка расшифровки: нецелое число")
            plain_indices.append(int(r))
    plain = ''.join(alphabet[i - 1] for i in plain_indices)
    return plain


# ------------------------------------------------------------
#                   Шифр Плэйфера (прямоугольная таблица)
# ------------------------------------------------------------

class Playfair:
    """Реализация шифра Плэйфера с таблицей произвольного размера rows × cols."""

    def __init__(self, alphabet, key, filler, rows, cols):
        """
        alphabet : строка уникальных символов (должна содержать ровно rows*cols букв)
        key      : ключевое слово (повторы игнорируются)
        filler   : фиктивная буква для вставки между одинаковыми
        rows, cols : размеры таблицы
        """
        self.alphabet = alphabet.upper()
        self.rows = rows
        self.cols = cols
        if len(self.alphabet) != self.rows * self.cols:
            raise ValueError(f"Длина алфавита ({len(self.alphabet)}) не равна {rows}×{cols}")
        self.filler = filler.upper()
        if self.filler not in self.alphabet:
            raise ValueError("Филлер должен присутствовать в алфавите")
        self.key = key.upper()
        self.table = self._build_table()

    def _build_table(self):
        """Построение таблицы rows × cols по ключу (заполнение по строкам)."""
        seen = set()
        key_chars = []
        for ch in self.key:
            if ch in self.alphabet and ch not in seen:
                seen.add(ch)
                key_chars.append(ch)
        for ch in self.alphabet:
            if ch not in seen:
                key_chars.append(ch)

        table = []
        for i in range(self.rows):
            row = key_chars[i * self.cols:(i + 1) * self.cols]
            table.append(row)
        return table

    def _find_coords(self, ch):
        """Возвращает (row, col) символа в таблице."""
        for r, row in enumerate(self.table):
            if ch in row:
                return r, row.index(ch)
        raise ValueError(f"Символ {ch} отсутствует в таблице")

    def _preprocess(self, text):
        """
        Подготовка открытого текста:
        - удаление символов не из алфавита,
        - вставка филлера между одинаковыми буквами,
        - добавление филлера в конец при нечётной длине.
        """
        text = text.upper()
        filtered = [ch for ch in text if ch in self.alphabet]
        if not filtered:
            return []

        i = 0
        result = []
        while i < len(filtered):
            result.append(filtered[i])
            if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
                result.append(self.filler)
            i += 1

        if len(result) % 2 != 0:
            result.append(self.filler)

        pairs = [(result[j], result[j + 1]) for j in range(0, len(result), 2)]
        return pairs

    def _encrypt_pair(self, a, b):
        """Шифрование одной биграммы."""
        r1, c1 = self._find_coords(a)
        r2, c2 = self._find_coords(b)

        if r1 == r2:                     # одна строка – сдвиг вправо
            c1 = (c1 + 1) % self.cols
            c2 = (c2 + 1) % self.cols
            return self.table[r1][c1], self.table[r2][c2]
        elif c1 == c2:                    # один столбец – сдвиг вниз
            r1 = (r1 + 1) % self.rows
            r2 = (r2 + 1) % self.rows
            return self.table[r1][c1], self.table[r2][c2]
        else:                             # прямоугольник – обмен столбцов
            return self.table[r1][c2], self.table[r2][c1]

    def _decrypt_pair(self, a, b):
        """Расшифрование одной биграммы."""
        r1, c1 = self._find_coords(a)
        r2, c2 = self._find_coords(b)

        if r1 == r2:                     # одна строка – сдвиг влево
            c1 = (c1 - 1) % self.cols
            c2 = (c2 - 1) % self.cols
            return self.table[r1][c1], self.table[r2][c2]
        elif c1 == c2:                    # один столбец – сдвиг вверх
            r1 = (r1 - 1) % self.rows
            r2 = (r2 - 1) % self.rows
            return self.table[r1][c1], self.table[r2][c2]
        else:                             # прямоугольник – обмен столбцов
            return self.table[r1][c2], self.table[r2][c1]

    def encrypt(self, text):
        pairs = self._preprocess(text)
        result = []
        for a, b in pairs:
            x, y = self._encrypt_pair(a, b)
            result.append(x + y)
        return ''.join(result)

    def decrypt(self, text):
        text = text.upper()
        if len(text) % 2 != 0:
            raise ValueError("Длина шифртекста должна быть чётной")
        pairs = [(text[i], text[i + 1]) for i in range(0, len(text), 2)]
        result = []
        for a, b in pairs:
            x, y = self._decrypt_pair(a, b)
            result.append(x + y)
        return ''.join(result)

    def print_table(self):
        print(f"\nТаблица шифрования ({self.rows}×{self.cols}):")
        for row in self.table:
            print(' '.join(row))


# ------------------------------------------------------------
#                   Интерфейс
# ------------------------------------------------------------

def matrix_cipher():
    alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    print("\n--- Матричный шифр ---")
    print("Используется алфавит (32 буквы):", alphabet)

    try:
        matrix = input_matrix()
        print("Матрица-ключ принята.")
    except Exception as e:
        print("Ошибка ввода матрицы:", e)
        return

    while True:
        print("\nМеню матричного шифра:")
        print("1. Зашифровать текст")
        print("2. Расшифровать числа")
        print("3. Вернуться в главное меню")
        choice = input("Ваш выбор: ")

        if choice == '1':
            text = input("Введите текст (только русские буквы): ").upper()
            filtered = [c for c in text if c in alphabet]
            if not filtered:
                print("Нет допустимых символов")
                continue
            text = ''.join(filtered)
            try:
                cipher = encrypt_matrix(text, matrix, alphabet)
                print("Зашифрованные числа:", ' '.join(str(x) for x in cipher))
            except Exception as e:
                print("Ошибка шифрования:", e)

        elif choice == '2':
            nums_str = input("Введите числа через пробел: ")
            try:
                nums = list(map(int, nums_str.split()))
            except ValueError:
                print("Неверный формат чисел")
                continue
            try:
                plain = decrypt_matrix(nums, matrix, alphabet)
                print("Расшифрованный текст:", plain)
            except Exception as e:
                print("Ошибка расшифровки:", e)

        elif choice == '3':
            break


def playfair_cipher():
    print("\n--- Шифр Плэйфера ---")
    print("Для русского алфавита без Ё, Й, Ъ (30 букв) будет использована таблица 5×6.")
    print("Вы можете ввести свой алфавит и размеры таблицы.")

    # Ввод алфавита
    alph = input("Алфавит (Enter для русского без ЁЙЪ): ").upper()
    if not alph:
        alph = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ"
        rows, cols = 5, 6
        print(f"Выбран русский алфавит (30 букв), таблица {rows}×{cols}")
    else:
        # Пользовательский алфавит – запрашиваем размеры
        print(f"Длина алфавита: {len(alph)}")
        ok = False
        while not ok:
            try:
                rows = int(input("Введите количество строк таблицы: "))
                cols = int(input("Введите количество столбцов таблицы: "))
                if rows * cols != len(alph):
                    print(f"Ошибка: {rows}×{cols} = {rows*cols}, а длина алфавита {len(alph)}. Повторите ввод.")
                else:
                    ok = True
            except ValueError:
                print("Введите целые числа.")

    key = input("Введите ключевое слово: ").upper()

    # Проверка, что ключ содержит только символы алфавита
    for ch in key:
        if ch not in alph:
            print(f"Символ '{ch}' отсутствует в алфавите")
            return

    # Анализ повторов в ключе
    seen = set()
    unique_key = []
    for ch in key:
        if ch not in seen:
            seen.add(ch)
            unique_key.append(ch)
    if len(unique_key) < len(key):
        print(f"В ключе были повторяющиеся символы. Уникальные символы ключа: {''.join(unique_key)}")
    else:
        print(f"Уникальные символы ключа: {''.join(unique_key)}")

    # Выбор филлера: по умолчанию первый символ алфавита
    default_filler = alph[0]
    filler = input(f"Введите фиктивную букву (Enter для '{default_filler}'): ").upper()
    if not filler:
        filler = default_filler
    if filler not in alph:
        print("Фиктивная буква должна присутствовать в алфавите")
        return

    try:
        pf = Playfair(alph, key, filler, rows, cols)
    except Exception as e:
        print("Ошибка создания шифра:", e)
        return

    pf.print_table()

    while True:
        print("\nМеню шифра Плэйфера:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Вернуться в главное меню")
        choice = input("Ваш выбор: ")

        if choice == '1':
            text = input("Введите открытый текст: ")
            try:
                cipher = pf.encrypt(text)
                print("Зашифрованный текст:", cipher)
            except Exception as e:
                print("Ошибка шифрования:", e)

        elif choice == '2':
            text = input("Введите шифртекст: ")
            try:
                plain = pf.decrypt(text)
                print("Расшифрованный текст:", plain)
            except Exception as e:
                print("Ошибка расшифровки:", e)

        elif choice == '3':
            break


def main():
    while True:
        print("\n========== Лабораторная работа: шифры блочной замены ==========")
        print("1. Матричный шифр")
        print("2. Шифр Плэйфера")
        print("0. Выход")
        choice = input("Выберите пункт: ")

        if choice == '1':
            matrix_cipher()
        elif choice == '2':
            playfair_cipher()
        elif choice == '0':
            print("Работа завершена.")
            break
        else:
            print("Неверный выбор, повторите.")


if __name__ == "__main__":
    main()