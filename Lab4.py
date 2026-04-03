import os
import random
import re

ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

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

# --- 10. ВЕРТИКАЛЬНАЯ ПЕРЕСТАНОВКА ---

def vertical_encrypt(text, key):
    key = clean_text(key)
    if not key: return "Ошибка: Ключ должен содержать русские буквы."
    
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
    if full_cols == 0: full_cols = cols

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

# --- 11. РЕШЕТКА КАРДАНО ---

STENCIL = [
    "1011111111",
    "0111010011",
    "1011101110",
    "1110111011",
    "1011111111",
    "1101100110"
]

def get_holes():
    holes = []
    for r in range(6):
        for c in range(10):
            if STENCIL[r][c] == '0':
                holes.append((r, c))
    return holes

def cardan_encrypt(text):
    holes = get_holes()
    capacity = len(holes) # 15 символов
    ciphertext = ""
    
    for i in range(0, len(text), capacity):
        block = text[i:i+capacity]
        if len(block) < capacity:
            block += "".join(random.choices(ALPHABET, k=capacity-len(block)))
            
        grid = [["" for _ in range(10)] for _ in range(6)]
        for k, (r, c) in enumerate(holes):
            grid[r][c] = block[k]
            
        for r in range(6):
            for c in range(10):
                if grid[r][c] == "":
                    grid[r][c] = random.choice(ALPHABET)
            ciphertext += "".join(grid[r])
    return ciphertext

def cardan_decrypt(ciphertext):
    holes = get_holes()
    plaintext = ""
    for i in range(0, len(ciphertext), 60):
        block = ciphertext[i:i+60]
        if len(block) < 60: break
        
        grid = [block[r*10:(r+1)*10] for r in range(6)]
        for r, c in holes:
            plaintext += grid[r][c]
    return plaintext

# --- 12. СЕТЬ ФЕЙСТЕЛЯ (МАГМА ГОСТ Р 34.12-2015) ---

PI = [
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1]
]

def g_func(a, k):
    temp = (a + k) % (1 << 32)
    out = 0
    for i in range(8):
        nibble = (temp >> (4 * i)) & 0xF
        out |= (PI[i][nibble] << (4 * i))
    return ((out << 11) | (out >> 21)) & 0xFFFFFFFF

def G_func(a1, a0, k):
    return a0, a1 ^ g_func(a0, k)

def expand_key(key_bytes):
    key_bytes = key_bytes.ljust(32, b'\0')[:32]
    K = [int.from_bytes(key_bytes[i*4:(i+1)*4], 'big') for i in range(8)]
    return K * 3 + K[::-1]

def magma_encrypt_block(block, keys):
    a1 = int.from_bytes(block[0:4], 'big')
    a0 = int.from_bytes(block[4:8], 'big')
    
    for i in range(31):
        a1, a0 = G_func(a1, a0, keys[i])
    temp = a0
    a0 = a1 ^ g_func(a0, keys[31])
    a1 = temp
    
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def magma_decrypt_block(block, keys):
    a1 = int.from_bytes(block[0:4], 'big')
    a0 = int.from_bytes(block[4:8], 'big')
    
    for i in range(31, 0, -1):
        a1, a0 = G_func(a1, a0, keys[i])
    temp = a0
    a0 = a1 ^ g_func(a0, keys[0])
    a1 = temp
    
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def magma_encrypt(text, key_str):
    keys = expand_key(key_str.encode('cp1251', errors='ignore'))
    text_bytes = text.encode('cp1251', errors='ignore')
    
    pad_len = (8 - len(text_bytes) % 8) % 8
    text_bytes += bytes([pad_len] * pad_len)
    
    cipher_bytes = b"".join([magma_encrypt_block(text_bytes[i:i+8], keys) for i in range(0, len(text_bytes), 8)])
    return cipher_bytes.hex()

def magma_decrypt(hex_str, key_str):
    try:
        cipher_bytes = bytes.fromhex(hex_str)
    except ValueError:
        return "Ошибка: Для Магмы зашифрованный текст должен быть в HEX-формате."
        
    keys = expand_key(key_str.encode('cp1251', errors='ignore'))
    text_bytes = b"".join([magma_decrypt_block(cipher_bytes[i:i+8], keys) for i in range(0, len(cipher_bytes), 8)])
    
    pad_len = text_bytes[-1]
    if 0 < pad_len <= 8:
        text_bytes = text_bytes[:-pad_len]
        
    return text_bytes.decode('cp1251', errors='ignore')


# --- ИНТЕРФЕЙС И МЕНЮ ---

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
        print("3. МАГМА (ГОСТ Р 34.12-2015)")
        print("0. Выход")
        
        choice = input("Выберите шифр: ")
        if choice == '0': break
        if choice not in ['1', '2', '3']:
            print("Неверный выбор.")
            continue
            
        action = input("Действие (1 - Шифровать, 2 - Расшифровать): ")
        text = get_input_data()
        if not text: continue
        
        if choice in ['1', '2'] and action == '1':
            text = clean_text(text) # Очистка только для шифрования классики

        if choice == '1':
            key = input("Введите ключ-слово (на русском): ")
            if action == '1': handle_output(vertical_encrypt(text, key))
            elif action == '2': handle_output(vertical_decrypt(text, key))
            
        elif choice == '2':
            print("*Ключом служит встроенный трафарет 6x10*")
            if action == '1': handle_output(cardan_encrypt(text))
            elif action == '2': handle_output(cardan_decrypt(text))
            
        elif choice == '3':
            key = input("Введите строковый ключ (до 32 символов): ")
            if action == '1':
                text = clean_text(text)
                handle_output(magma_encrypt(text, key))
            elif action == '2': 
                handle_output(magma_decrypt(text.strip(), key))



if __name__ == "__main__":
    main()