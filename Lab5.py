import math
import os
import struct
import sys

# =====================================================================
#   1. ЛОГИКА МАГМЫ (ПОЛНОСТЬЮ ИЗ ВАШЕГО КОДА)
# =====================================================================
PI = [
    [12, 4,  6,  2, 10,  5, 11,  9, 14,  8, 13,  7,  0,  3, 15,  1],
    [ 6,  8,  2,  3,  9, 10,  5, 12,  1, 14,  4,  7, 11, 13,  0, 15],
    [11,  3,  5,  8,  2, 15, 10, 13, 14,  1,  7,  4, 12,  9,  6,  0],
    [12,  8,  2,  1, 13,  4, 15,  6,  7,  0, 10,  5,  3, 14,  9, 11],
    [ 7, 15,  5, 10,  8,  1,  6, 13,  0,  9,  3, 14, 11,  4,  2, 12],
    [ 5, 13, 15,  6,  9,  2, 12, 10, 11,  7,  8,  1,  4,  3, 14,  0],
    [ 8, 14,  2,  5,  6,  9,  1, 12, 15,  4, 11,  0, 13, 10,  3,  7],
    [ 1,  7, 14, 13,  0,  5,  8,  3,  4, 15, 10,  6,  9, 12, 11,  2],
]

def t_transform(x: int) -> int:
    result = 0
    for i in range(8):
        nibble = (x >> (4 * i)) & 0xF
        result |= PI[i][nibble] << (4 * i)
    return result

def left_shift_11(x: int) -> int:
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def g(k: int, a: int) -> int:
    return left_shift_11(t_transform((a + k) & 0xFFFFFFFF))

def key_schedule(key_bytes: bytes) -> list:
    K = list(struct.unpack('>8I', key_bytes))
    return K * 3 + K[::-1]

def magma_encrypt_block(block: bytes, round_keys: list) -> bytes:
    a1, a0 = struct.unpack('>II', block)
    for i in range(31):
        a1, a0 = a0, g(round_keys[i], a0) ^ a1
    a1 = g(round_keys[31], a0) ^ a1
    return struct.pack('>II', a1, a0)

def ctr_process(data: bytes, key: bytes, iv: bytes) -> bytes:
    round_keys = key_schedule(key)
    ctr = int.from_bytes(iv, 'big')
    out = bytearray()
    for i in range(0, len(data), 8):
        gamma = magma_encrypt_block(ctr.to_bytes(8, 'big'), round_keys)
        chunk = data[i:i+8]
        out.extend(b ^ gm for b, gm in zip(chunk, gamma))
        ctr = (ctr + 1) & 0xFFFFFFFFFFFFFFFF
    return bytes(out)

# =====================================================================
#   2. ЛОГИКА ШЕННОНА (Алгоритм 13)
# =====================================================================
RUS_UPPER = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RUS_LOWER = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

def shannon_crypt(text, a, c, t0, encrypt=True):
    res = []
    t = t0
    for char in text:
        if char in RUS_UPPER:
            t = (a * t + c) % 32
            shift = t if encrypt else -t
            idx = (RUS_UPPER.index(char) + shift) % 32
            res.append(RUS_UPPER[idx])
        elif char in RUS_LOWER:
            t = (a * t + c) % 32
            shift = t if encrypt else -t
            idx = (RUS_LOWER.index(char) + shift) % 32
            res.append(RUS_LOWER[idx])
        else:
            res.append(char)
    return "".join(res)

# =====================================================================
#   3. ИНТЕРФЕЙС
# =====================================================================

def handle_shannon():
    print("\n--- Одноразовый блокнот К.Шеннона ---")
    print("1. Зашифровать\n2. Расшифровать\n3. Зашифровать файл\n4. Расшифровать файл")
    sub = input("Выберите пункт: ")
    try:
        while True:
            a = int(input("Введите A (нечетное, не 1): "))
            if a % 2 != 0 and a != 1: break
            print("Ошибка: A должно быть нечетным и не равным 1.")
            
        while True:
            c = int(input("Введите C (взаимно простое с 32, не 1): "))
            if c % 2 != 0 and c != 1: break
            print("Ошибка: C должно быть нечетным (взаимно простым с 32) и не равным 1.")
            
        t0 = int(input("Введите T0: "))
        
        if sub in ['1', '2']:
            text = input("Введите текст (русский): ")
            res = shannon_crypt(text, a, c, t0, encrypt=(sub == '1'))
            print(f"Результат: {res}")
        elif sub in ['3', '4']:
            f_in = input("Введите имя файла: ")
            if os.path.exists(f_in):
                with open(f_in, 'r', encoding='utf-8') as f: content = f.read()
                res = shannon_crypt(content, a, c, t0, encrypt=(sub == '3'))
                with open("shannon_res.txt", 'w', encoding='utf-8') as f: f.write(res)
                print("Готово! Результат в shannon_res.txt")
    except ValueError:
        print("Ошибка ввода.")

def handle_magma():
    print("\n--- Гаммирование ГОСТ (Магма) ---")
    print("1. Зашифровать\n2. Расшифровать\n3. Зашифровать файл\n4. Расшифровать файл")
    sub = input("Выберите пункт: ")
    
    k_hex = input("Введите ключ (K) в HEX: ").strip()
    k_bytes = bytes.fromhex(k_hex)
    
    s_raw = input("Введите синхропосылку (S): ").strip()
    s_padded = s_raw.ljust(16, '0')[:16]
    s_bytes = bytes.fromhex(s_padded)

    if sub in ['1', '2']:
        data_hex = input("Введите входной блок (HEX): ").strip()
        data_bytes = bytes.fromhex(data_hex)
        res = ctr_process(data_bytes, k_bytes, s_bytes)
        print(f"Результат (HEX): {res.hex()}")
    elif sub in ['3', '4']:
        f_in = input("Введите имя файла: ")
        if os.path.exists(f_in):
            with open(f_in, 'rb') as f: data = f.read()
            res = ctr_process(data, k_bytes, s_bytes)
            with open("magma_res.bin", 'wb') as f: f.write(res)
            print("Готово! Результат в magma_res.bin")

def main():
    while True:
        print("\n" + "="*50)
        print("1. Одноразовый блокнот К.Шеннона")
        print("2. Гаммирование ГОСТ Р 34.13-2015 (Магма)")
        print("3. Выход")
        print("="*50)
        
        choice = input("Выберите пункт меню: ")
        if choice == '1': handle_shannon()
        elif choice == '2': handle_magma()
        elif choice == '3': break
        else: continue
            
        cont = input("\nПродолжить выполнение всей программы? (да/нет): ").lower()
        if cont not in ['да', 'д', 'yes', 'y']: break

if __name__ == "__main__":
    main()