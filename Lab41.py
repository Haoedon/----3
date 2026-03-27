# -*- coding: utf-8 -*-
"""
Лабораторная работа №4
Реализация классических и современных шифров
Пункт 3: МАГМА (ГОСТ Р 34.12-2015) - Сеть Фейстеля
"""
import os
import random
import re

# ==========================================
# ОБЩИЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

def clean_text(text):
    """Очистка текста: убираем 'ё', оставляем только русские буквы."""
    text = text.upper().replace('Ё', 'Е')
    return re.sub(r'[^А-Я]', '', text)

def read_file(filepath):
    if not os.path.exists(filepath):
        print("[-] Ошибка: Файл не найден.")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Результат успешно сохранен в файл: {filepath}")

def input_hex(prompt, expected_length, description):
    """Запрашивает HEX строку с немедленной проверкой"""
    while True:
        value = input(prompt).strip().lower()
        
        # Проверка длины
        if len(value) != expected_length:
            print(f"Ошибка: {description} должен быть {expected_length} HEX символов!")
            print(f"  Вы ввели {len(value)} символов. Попробуйте снова.")
            continue
        
        # Проверка на валидность HEX
        try:
            int(value, 16)
            return value
        except ValueError:
            print(f"Ошибка: {description} должен содержать только HEX символы (0-9, a-f)!")
            continue

# ==========================================
# 1. ВЕРТИКАЛЬНАЯ ПЕРЕСТАНОВКА
# ==========================================
def vertical_encrypt(text, key):
    key = clean_text(key)
    if not key: 
        return "Ошибка: Ключ должен содержать русские буквы."
    cols = len(key)
    grid = [text[i:i+cols] for i in range(0, len(text), cols)]
    key_order = sorted(range(len(key)), key=lambda x: key[x])

    ciphertext = ""
    for col in key_order:
        for row in grid:
            if col < len(row):
                ciphertext += row[col]
    return ciphertext

def vertical_decrypt(ciphertext, key):
    key = clean_text(key)
    cols = len(key)
    rows = (len(ciphertext) + cols - 1) // cols
    full_cols = len(ciphertext) % cols
    if full_cols == 0: 
        full_cols = cols
    key_order = sorted(range(len(key)), key=lambda x: key[x])
    col_lengths = [rows if i < full_cols else rows - 1 for i in range(cols)]

    grid_cols = {}
    idx = 0
    for col in key_order:
        length = col_lengths[col]
        grid_cols[col] = ciphertext[idx:idx+length]
        idx += length

    plaintext = ""
    for r in range(rows):
        for c in range(cols):
            if r < col_lengths[c]:
                plaintext += grid_cols[c][r]
    return plaintext

# ==========================================
# 11. РЕШЕТКА КАРДАНО
# ==========================================
# ==========================================
# 11. РЕШЕТКА КАРДАНО (ДЛИНА СОХРАНЯЕТСЯ)
# ==========================================

STENCIL = [
    "1011111111",
    "0111010011",
    "1011101110",
    "1110111011",
    "1011111111",
    "1101100110"
]

def get_holes():
    """Возвращает координаты отверстий в трафарете (15 штук)"""
    holes = []
    for r in range(6):
        for c in range(10):
            if STENCIL[r][c] == '0':
                holes.append((r, c))
    return holes

def cardan_decrypt(ciphertext):
    """
    Расшифрование решёткой Кардано.
    Вход: блоки по 60 символов.
    Выход: текст той же длины, что и вход (60 символов на блок).
    """
    holes = get_holes()
    plaintext = ""
    block_size = 60  # Размер блока шифротекста
    
    for i in range(0, len(ciphertext), block_size):
        block = ciphertext[i:i+block_size]
        
        # Если блок неполный — оставляем как есть
        if len(block) < block_size:
            plaintext += block
            continue
        
        # Восстанавливаем сетку 6x10
        grid = [block[r*10:(r+1)*10] for r in range(6)]
        
        # Извлекаем символы из отверстий (15 символов)
        decrypted_block = ""
        for r, c in holes:
            decrypted_block += grid[r][c]
        
        # ДОПОЛНЯЕМ до 60 символов СЛУЧАЙНЫМИ БУКВАМИ, чтобы длина совпадала
        padding_needed = block_size - len(decrypted_block)
        if padding_needed > 0:
            decrypted_block += "".join(random.choices(ALPHABET, k=padding_needed))
        
        plaintext += decrypted_block
    
    return plaintext
# ==========================================
# 3. МАГМА (ГОСТ Р 34.12-2015) - СЕТЬ ФЕЙСТЕЛЯ
# ==========================================
# Таблицы замен (S-блоки) согласно ГОСТ Р 34.12-2015
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

def t_transform(a):
    """Преобразование t: V32 → V32 (S-блоки)"""
    result = 0
    for i in range(8):
        nibble = (a >> (4 * i)) & 0x0F
        substituted = PI[i][nibble]
        result |= (substituted << (4 * i))
    return result

def rotate_left_11(value):
    """Циклический сдвиг влево на 11 бит"""
    value &= 0xFFFFFFFF
    return ((value << 11) | (value >> 21)) & 0xFFFFFFFF

def g_transform(k, a):
    """Преобразование g[k]: V32 → V32"""
    temp = (a + k) & 0xFFFFFFFF
    temp = t_transform(temp)
    temp = rotate_left_11(temp)
    return temp

def G_transform(k, a1, a0):
    """Преобразование G[k]: V32 × V32 → V32 × V32"""
    new_a1 = a0
    new_a0 = g_transform(k, a0) ^ a1
    return new_a1, new_a0

def G_star_transform(k, a1, a0):
    """Преобразование G*[k]: V32 × V32 → V64 (последний раунд)"""
    result_high = g_transform(k, a0) ^ a1
    result_low = a0
    return result_high, result_low

def generate_round_keys(key_hex):
    """Генерирует 32 итерационных ключа из 256-битного ключа (HEX)"""
    key_bytes = bytes.fromhex(key_hex)
    
    if len(key_bytes) != 32:
        raise ValueError("Ключ должен быть длиной 64 символа HEX (256 бит)")

    # Разбиваем ключ на 8 подключей по 32 бита
    K = []
    for i in range(8):
        k_bytes = key_bytes[i*4:(i+1)*4]
        K.append(int.from_bytes(k_bytes, byteorder='big'))

    # Формируем 32 итерационных ключа
    round_keys = []
    for i in range(8): 
        round_keys.append(K[i])      # K1...K8
    for i in range(8): 
        round_keys.append(K[i])      # K9...K16
    for i in range(8): 
        round_keys.append(K[i])      # K17...K24
    for i in range(7, -1, -1): 
        round_keys.append(K[i])      # K25...K32 (обратный порядок)

    return round_keys

def magma_encrypt_block(a, round_keys):
    """Шифрует 64-битное число"""
    if isinstance(a, str):
        a = int(a, 16)
    
    a1 = (a >> 32) & 0xFFFFFFFF
    a0 = a & 0xFFFFFFFF

    # 31 раунд с G
    for i in range(31):
        a1, a0 = G_transform(round_keys[i], a1, a0)

    # 32-й раунд с G*
    b1, b0 = G_star_transform(round_keys[31], a1, a0)

    return (b1 << 32) | b0

def magma_decrypt_block(b, round_keys):
    """Расшифровывает 64-битное число"""
    if isinstance(b, str):
        b = int(b, 16)
    
    b1 = (b >> 32) & 0xFFFFFFFF
    b0 = b & 0xFFFFFFFF

    # 31 раунд с G (ключи в обратном порядке K32...K2)
    for i in range(31, 0, -1):
        b1, b0 = G_transform(round_keys[i], b1, b0)

    # 32-й раунд с G* (ключ K1)
    a1, a0 = G_star_transform(round_keys[0], b1, b0)

    return (a1 << 32) | a0

def test_gost_example():
    """Тестирует алгоритм на контрольном примере из ГОСТ Р 34.12-2015"""
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ НА КОНТРОЛЬНОМ ПРИМЕРЕ ИЗ ГОСТ Р 34.12-2015 (А.2)")
    print("=" * 80)
    
    # Ключ из примера A.2.3
    K = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    print(f"\nКлюч (256 бит):\n{K}")

    round_keys = generate_round_keys(K)

    # Проверка раундовых ключей
    expected_keys = {
        1: 0xffeeddcc, 9: 0xffeeddcc, 17: 0xffeeddcc, 25: 0xfcfdfeff,
        8: 0xfcfdfeff, 16: 0xfcfdfeff, 24: 0xfcfdfeff, 32: 0xffeeddcc
    }

    print("\nВыборочная проверка раундовых ключей:")
    all_correct = True
    for i in sorted(expected_keys.keys()):
        expected = expected_keys[i]
        actual = round_keys[i-1]
        status = "✓" if actual == expected else "✗"
        print(f"  K{i:2d} = {actual:08x} (ожидается {expected:08x}) {status}")
        if actual != expected:
            all_correct = False

    if not all_correct:
        print("\nОШИБКА: Раундовые ключи не совпадают!")
        return False

    # Открытый текст из примера A.2.4
    a = 0xfedcba9876543210
    print(f"\n{'-'*80}")
    print("ШИФРОВАНИЕ:")
    print(f"Открытый текст (64 бит):    {a:016x}")

    b = magma_encrypt_block(a, round_keys)

    print(f"Зашифрованный текст:        {b:016x}")
    print(f"Ожидается по ГОСТ:          4ee901e5c2d8ca3d")

    if b == 0x4ee901e5c2d8ca3d:
        print("ШИФРОВАНИЕ УСПЕШНО!")
    else:
        print("ОШИБКА ШИФРОВАНИЯ!")
        return False

    # Расшифрование
    print(f"\n{'-'*80}")
    print("РАСШИФРОВАНИЕ:")
    d = magma_decrypt_block(b, round_keys)

    print(f"Расшифрованный текст:       {d:016x}")
    print(f"Ожидается (исходный текст): {a:016x}")

    if d == a:
        print("РАСШИФРОВАНИЕ УСПЕШНО!")
        print("\n" + "=" * 80)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ! АЛГОРИТМ РАБОТАЕТ КОРРЕКТНО!")
        print("=" * 80)
        return True
    else:
        print("ОШИБКА РАСШИФРОВАНИЯ!")
        return False

# ==========================================
# ИНТЕРФЕЙС И МЕНЮ
# ==========================================
def get_input_data():
    choice = input("Ввод текста (1 - из консоли, 2 - из файла): ")
    if choice == '1':
        return input("Введите текст: ")
    elif choice == '2':
        path = input("Введите путь к файлу (например, input.txt): ")
        return read_file(path)
    return None

def handle_output(result):
    print(f"\nРезультат:\n{result}\n")
    choice = input("Сохранить результат в файл? (y/n): ")
    if choice.lower() == 'y':
        path = input("Введите путь для сохранения (например, output.txt): ")
        write_file(path, result)

def main():
    while True:
        print("\n=== КРИПТОГРАФИЧЕСКАЯ ПРОГРАММА ===")
        print("1. Вертикальная перестановка")
        print("2. Решетка Кардано (трафарет 6x10)")
        print("3. МАГМА (ГОСТ Р 34.12-2015) - Шифр Фейстеля")
        print("0. Выход")
        
        choice = input("Выберите шифр: ")
        
        if choice == '0':
            print("\nДо свидания!")
            break
            
        if choice not in ['1', '2', '3']:
            print("Неверный выбор.")
            continue
        
        # Специфичное меню для МАГМА
        if choice == '3':
            print("\n--- МЕНЮ МАГМА (ГОСТ Р 34.12-2015) ---")
            print("1 - Зашифровать HEX блок")
            print("2 - Расшифровать HEX блок")
            print("3 - Тестирование (ГОСТ векторы)")
            print("0 - Назад")
            
            action = input("Ваш выбор: ")
            
            if action == '0':
                continue
            elif action == '3':
                test_gost_example()
                continue
            elif action not in ['1', '2']:
                print("Неверный выбор.")
                continue
            
            print("\n" + "-" * 80)
            if action == '1':
                print("ШИФРОВАНИЕ (МАГМА)")
                plaintext = input_hex(
                    "Введите открытый текст (16 HEX символов): ",
                    16,
                    "Открытый текст"
                )
            else:
                print("РАСШИФРОВАНИЕ (МАГМА)")
                plaintext = input_hex(
                    "Введите зашифрованный текст (16 HEX символов): ",
                    16,
                    "Зашифрованный текст"
                )
            
            key = input_hex(
                "Введите ключ (64 HEX символа, 256 бит): ",
                64,
                "Ключ"
            )
            
            round_keys = generate_round_keys(key)
            data_int = int(plaintext, 16)
            
            if action == '1':
                result_int = magma_encrypt_block(data_int, round_keys)
                label = "Зашифрованный текст"
            else:
                result_int = magma_decrypt_block(data_int, round_keys)
                label = "Расшифрованный текст"
            
            print(f"\n{'='*80}")
            print(f"Входные данные:        {data_int:016x}")
            print(f"Ключ:                  {key}")
            print(f"{label}: {result_int:016x}")
            print(f"{'='*80}")
            
            # Опция сохранения
            save = input("Сохранить результат в файл? (y/n): ")
            if save.lower() == 'y':
                path = input("Путь к файлу: ")
                write_file(path, f"{result_int:016x}")
            continue

        # Стандартное меню для шифров 1 и 2
        action = input("Действие (1 - Шифровать, 2 - Расшифровать): ")
        text = get_input_data()
        
        if not text:
            continue
        
        if choice in ['1', '2'] and action == '1':
            text = clean_text(text)

        if choice == '1':
            key = input("Введите ключ-слово (на русском): ")
            if action == '1':
                handle_output(vertical_encrypt(text, key))
            elif action == '2':
                handle_output(vertical_decrypt(text, key))
            
        elif choice == '2':
            print("*Ключом служит встроенный трафарет 6x10*")
            print("*Длина расшифрованного текста = длине шифротекста*")
        if action == '1': 
            handle_output(cardan_encrypt(text))
        elif action == '2': 
            
            handle_output(cardan_decrypt(text))


if __name__ == "__main__":
    main()