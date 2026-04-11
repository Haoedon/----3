import sys
from itertools import zip_longest

# =====================================================================
# КОНСТАНТЫ
# =====================================================================
ALPHABET = [
    "а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
    "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
    "ъ", "ы", "ь", "э", "ю", "я"
]

PUNCT_MAP = {
    '.': 'тчк', ',': 'зпт', ';': 'тчз', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз', "'": 'апстр', ' ': 'прбл'
}
REV_PUNCT_MAP = {v: k for k, v in PUNCT_MAP.items()}


# =====================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =====================================================================
def majority(x, y, z):
    """Мажоритарная функция: возвращает 1, если большинства битов равно 1."""
    return (x & y) | (x & z) | (y & z)


# =====================================================================
# A5/2 (ПРОЦЕДУРНАЯ РЕАЛИЗАЦИЯ)
# =====================================================================
def a52_clock_all(state, input_bit):
    """Принудительный сдвиг всех четырёх регистров с входным битом."""
    r1, r2, r3, r4 = state['R1'], state['R2'], state['R3'], state['R4']
    
    nb1 = r1[13] ^ r1[16] ^ r1[17] ^ r1[18] ^ input_bit
    nb2 = r2[20] ^ r2[21] ^ input_bit
    nb3 = r3[7] ^ r3[20] ^ r3[21] ^ r3[22] ^ input_bit
    nb4 = r4[11] ^ r4[16] ^ input_bit

    state['R1'] = [nb1] + r1[:-1]
    state['R2'] = [nb2] + r2[:-1]
    state['R3'] = [nb3] + r3[:-1]
    state['R4'] = [nb4] + r4[:-1]


def a52_clock_stop_go(state, generate_output=False):
    """Условный сдвиг R1-R3 по сигналу от R4. Возвращает бит гаммы, если нужно."""
    r1, r2, r3, r4 = state['R1'], state['R2'], state['R3'], state['R4']
    
    f = majority(r4[3], r4[7], r4[10])
    shift_r1 = (r4[10] == f)
    shift_r2 = (r4[3]  == f)
    shift_r3 = (r4[7]  == f)

    # R4 сдвигается всегда
    nb4 = r4[11] ^ r4[16]
    state['R4'] = [nb4] + r4[:-1]

    if shift_r1:
        nb1 = r1[13] ^ r1[16] ^ r1[17] ^ r1[18]
        state['R1'] = [nb1] + r1[:-1]
    if shift_r2: 
        nb2 = r2[20] ^ r2[21]
        state['R2'] = [nb2] + r2[:-1]
    if shift_r3:
        nb3 = r3[7] ^ r3[20] ^ r3[21] ^ r3[22]
        state['R3'] = [nb3] + r3[:-1]

    if generate_output:
        out = r1[18] ^ r2[21] ^ r3[22]
        maj1 = majority(r1[12], r1[14], r1[15])
        maj2 = majority(r2[9],  r2[13], r2[16])
        maj3 = majority(r3[13], r3[16], r3[18])
        return out ^ maj1 ^ maj2 ^ maj3
    return None


def a52_initialize(key_bits, frame_bits):
    """Инициализация состояния A5/2: загрузка ключа, кадра, 100 тактов перемешивания."""
    state = {'R1': [0]*19, 'R2': [0]*22, 'R3': [0]*23, 'R4': [0]*17}

    for b in key_bits:
        a52_clock_all(state, b)
    for b in frame_bits:
        a52_clock_all(state, b)

    # Предотвращение нулевого состояния управляющего регистра
    state['R4'][3] = 1
    state['R4'][7] = 1
    state['R4'][10] = 1

    # Стандарт GSM требует 100 холостых тактов
    for _ in range(100):
        a52_clock_stop_go(state, generate_output=False)
    return state


def a52_generate_keystream(state, length):
    """Генерация гаммы заданной длины."""
    return [a52_clock_stop_go(state, generate_output=True) for _ in range(length)]


def encrypt_data_a52(data_bits, key_bits, start_frame=0):
    result = ""
    frame = start_frame
    key_list = [int(b) for b in key_bits]
    
    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        frame_list = [int(b) for b in format(frame, '022b')]
        
        state = a52_initialize(key_list, frame_list)
        gamma = a52_generate_keystream(state, len(block))
        
        xored = "".join(str(int(block[j]) ^ gamma[j]) for j in range(len(block)))
        result += xored
        frame += 1
    return result


def decrypt_data_a52(cipher_bits, key_bits, start_frame=0):
    return encrypt_data_a52(cipher_bits, key_bits, start_frame)


def encrypt_text_a52(plaintext, key_bits, start_frame=0):
    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data_a52(data_bits, key_bits, start_frame)
    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\nИТОГОВЫЙ РЕЗУЛЬТАТ (A5/2): {formatted}")
    return formatted


def decrypt_text_a52(ciphertext, key_bits, start_frame=0):
    bits = ciphertext.replace(' ', '')
    plain_bits = decrypt_data_a52(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)
    print(f"\nИТОГОВЫЙ ТЕКСТ (A5/2): {final_text}")
    return final_text


# =====================================================================
# A5/1 (ПРОЦЕДУРНАЯ РЕАЛИЗАЦИЯ)
# =====================================================================
def generate_gamma_a51(key_bits, frame_num):
    r1, r2, r3 = [0]*19, [0]*22, [0]*23

    for bit in map(int, key_bits):
        r1 = [r1[13]^r1[16]^r1[17]^r1[18]^bit] + r1[:-1]
        r2 = [r2[20]^r2[21]^bit] + r2[:-1]
        r3 = [r3[7]^r3[20]^r3[21]^r3[22]^bit] + r3[:-1]

    frame_bits = format(frame_num, '022b')
    for bit in map(int, frame_bits):
        r1 = [r1[13]^r1[16]^r1[17]^r1[18]^bit] + r1[:-1]
        r2 = [r2[20]^r2[21]^bit] + r2[:-1]
        r3 = [r3[7]^r3[20]^r3[21]^r3[22]^bit] + r3[:-1]

    for _ in range(100):
        maj = 1 if (r1[8] + r2[10] + r3[10]) >= 2 else 0
        if r1[8] == maj: r1 = [r1[13]^r1[16]^r1[17]^r1[18]] + r1[:-1]
        else:            r1 = [r1[18]] + r1[:-1]
        if r2[10] == maj: r2 = [r2[20]^r2[21]] + r2[:-1]
        else:             r2 = [r2[21]] + r2[:-1]
        if r3[10] == maj: r3 = [r3[7]^r3[20]^r3[21]^r3[22]] + r3[:-1]
        else:             r3 = [r3[22]] + r3[:-1]

    gamma = []
    for _ in range(114):
        maj = 1 if (r1[8] + r2[10] + r3[10]) >= 2 else 0
        gamma.append(r1[18] ^ r2[21] ^ r3[22])
        if r1[8] == maj: r1 = [r1[13]^r1[16]^r1[17]^r1[18]] + r1[:-1]
        else:            r1 = [r1[18]] + r1[:-1]
        if r2[10] == maj: r2 = [r2[20]^r2[21]] + r2[:-1]
        else:             r2 = [r2[21]] + r2[:-1]
        if r3[10] == maj: r3 = [r3[7]^r3[20]^r3[21]^r3[22]] + r3[:-1]
        else:             r3 = [r3[22]] + r3[:-1]
    return gamma


def encrypt_data_a51(data_bits, key_bits, start_frame=0):
    result = ""
    frame = start_frame
    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        gamma = generate_gamma_a51(key_bits, frame)
        xored = "".join(str(int(block[j]) ^ gamma[j]) for j in range(len(block)))
        result += xored
        frame += 1
    return result


def decrypt_data_a51(cipher_bits, key_bits, start_frame=0):
    return encrypt_data_a51(cipher_bits, key_bits, start_frame)


def encrypt_text_a51(plaintext, key_bits, start_frame=0):
    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data_a51(data_bits, key_bits, start_frame)
    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\nИТОГОВЫЙ РЕЗУЛЬТАТ (A5/1): {formatted}")
    return formatted


def decrypt_text_a51(ciphertext, key_bits, start_frame=0):
    bits = ciphertext.replace(' ', '')
    plain_bits = decrypt_data_a51(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)
    print(f"\nИТОГОВЫЙ ТЕКСТ (A5/1): {final_text}")
    return final_text


# =====================================================================
# ПРЕОБРАЗОВАНИЕ ТЕКСТА И КЛЮЧЕЙ
# =====================================================================
def text_to_bits(text):
    print(f"\n--- ПРЕОБРАЗОВАНИЕ ТЕКСТА В БИТЫ ---")
    result = ""
    for ch in text:
        if ch not in ALPHABET:
            print(f"  Предупреждение: символ '{ch}' не найден в алфавите, пропускается.")
            continue
        idx = ALPHABET.index(ch)
        bits = format(idx, '05b')
        result += bits
    print(f"  Итоговая битовая строка: {result}")
    return result


def bits_to_text(bits):
    print(f"\n--- ПРЕОБРАЗОВАНИЕ БИТОВ В ТЕКСТ ---")
    chunks = [bits[i:i+5] for i in range(0, len(bits), 5) if len(bits[i:i+5]) == 5]
    result = ""
    for chunk in chunks:
        idx = int(chunk, 2)
        result += ALPHABET[idx]
    return result


def normalize_text(text):
    print(f"\n--- НОРМАЛИЗАЦИЯ ТЕКСТА ---")
    text = text.lower().replace('ё', 'е')
    for punct, repl in PUNCT_MAP.items():
        text = text.replace(punct, repl)
    print(f"  Результат: {text}")
    return text


def denormalize_text(text):
    print(f"\n--- ВОССТАНОВЛЕНИЕ ЗНАКОВ ---")
    for word, punct in REV_PUNCT_MAP.items():
        text = text.replace(word, punct)
    print(f"  Результат: {text}")
    return text


def get_key_bits():
    print("\n" + "=" * 70 + "\nВВОД КЛЮЧА\n" + "=" * 70)
    key_word = input("Ключ (8 русских букв): ").strip().lower()
    if len(key_word) < 8:
        print("Ошибка: минимум 8 букв")
        sys.exit(1)
    key_word = key_word[:8]
    key_bits = "".join(''.join(format(b, '08b') for b in ch.encode('utf-8')) for ch in key_word)
    final_key = key_bits[:64]
    print(f"Итоговый 64-битный ключ: {final_key}")
    return final_key


def get_frame_number():
    try:
        return int(input("Номер кадра (по умолчанию 0): ").strip() or "0")
    except ValueError:
        return 0


# =====================================================================
# ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ
# =====================================================================
def main():
    while True:
        print("\n" + "=" * 50)
        print("ПОТОЧНЫЙ ШИФР A5 (A5/1 и A5/2)")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        print("=" * 50)

        choice = input("Выберите пункт меню: ").strip()

        if choice in ['1', '2']:
            algo = input("Выберите алгоритм (1 - A5/1, 2 - A5/2): ").strip()
            if algo not in ['1', '2']:
                print("Ошибка выбора.")
                continue

            text = input("Введите текст или биты: ").strip()
            key_bits = get_key_bits()
            frame_num = get_frame_number()
            
            if choice == '1':
                if algo == '1': encrypt_text_a51(text, key_bits, frame_num)
                else:           encrypt_text_a52(text, key_bits, frame_num)
            elif choice == '2':
                if algo == '1': decrypt_text_a51(text, key_bits, frame_num)
                else:           decrypt_text_a52(text, key_bits, frame_num)
            
        elif choice == '3':
            print("Выход из программы.")
            break
        else:
            print("Неверный пункт меню.")

        if input("\nПродолжить? (да/нет): ").lower() not in ['да', 'д', 'y']:
            break


if __name__ == "__main__":
    main()