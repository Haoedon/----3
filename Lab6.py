import sys
from itertools import zip_longest

# =====================================================================
#   КОНСТАНТЫ
# =====================================================================
ALPHABET = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
            "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
            "ъ", "ы", "ь", "э", "ю", "я"]

PUNCT_MAP = {
    '.': 'тчк', ',': 'зпт', ';': 'тчз', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз', "'": 'апстр', ' ': 'прбл'
}
REV_PUNCT_MAP = {v: k for k, v in PUNCT_MAP.items()}


# =====================================================================
#   РЕГИСТРЫ A5/2 (Добавлено из a5_2.py)
# =====================================================================
class A52Cipher:
    def __init__(self):
        # Регистры хранятся как списки битов от младшего (индекс 0) к старшему (индекс len-1)
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.R4 = [0] * 17

    def majority(self, x, y, z):
        """Мажоритарная функция: большинство из трёх битов."""
        return (x & y) | (x & z) | (y & z)

    def clock_all(self, input_bit):
        """
        Один такт, в котором все четыре регистра сдвигаются,
        а новый бит вычисляется как XOR обратной связи и входного бита.
        """
        nb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18] ^ input_bit
        nb2 = self.R2[20] ^ self.R2[21] ^ input_bit
        nb3 = self.R3[7]  ^ self.R3[20] ^ self.R3[21] ^ self.R3[22] ^ input_bit
        nb4 = self.R4[11] ^ self.R4[16] ^ input_bit

        self.R1 = [nb1] + self.R1[:-1]
        self.R2 = [nb2] + self.R2[:-1]
        self.R3 = [nb3] + self.R3[:-1]
        self.R4 = [nb4] + self.R4[:-1]

    def clock_stop_go(self, generate_output=False):
        """
        Один такт с управлением от R4.
        generate_output = True – возвращает выходной бит гаммы.
        """
        f = self.majority(self.R4[3], self.R4[7], self.R4[10])

        shift_r1 = (self.R4[10] == f)
        shift_r2 = (self.R4[3]  == f)
        shift_r3 = (self.R4[7]  == f)

        nb4 = self.R4[11] ^ self.R4[16]
        self.R4 = [nb4] + self.R4[:-1]

        if shift_r1:
            nb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18]
            self.R1 = [nb1] + self.R1[:-1]
        if shift_r2:
            nb2 = self.R2[20] ^ self.R2[21]
            self.R2 = [nb2] + self.R2[:-1]
        if shift_r3:
            nb3 = self.R3[7] ^ self.R3[20] ^ self.R3[21] ^ self.R3[22]
            self.R3 = [nb3] + self.R3[:-1]

        if generate_output:
            out = self.R1[18] ^ self.R2[21] ^ self.R3[22]
            maj1 = self.majority(self.R1[12], self.R1[14], self.R1[15])
            maj2 = self.majority(self.R2[9],  self.R2[13], self.R2[16])
            maj3 = self.majority(self.R3[13], self.R3[16], self.R3[18])
            return out ^ maj1 ^ maj2 ^ maj3
        return None

    def initialize(self, key_bits, frame_bits):
        """
        Загрузка 64‑битного ключа и 22‑битного номера кадра,
        затем 100 тактов перемешивания.
        """
        self.R1 = [0]*19
        self.R2 = [0]*22
        self.R3 = [0]*23
        self.R4 = [0]*17

        for b in key_bits:
            self.clock_all(b)

        for b in frame_bits:
            self.clock_all(b)

        self.R4[3] = 1
        self.R4[7] = 1
        self.R4[10] = 1

        for _ in range(64):
            self.clock_stop_go(generate_output=False)

    def generate_keystream(self, length):
        ks = []
        for _ in range(length):
            ks.append(self.clock_stop_go(generate_output=True))
        return ks


# =====================================================================
#   ПРЕОБРАЗОВАНИЕ ТЕКСТА
# =====================================================================
def text_to_bits(text: str) -> str:
    print(f"\n--- ПРЕОБРАЗОВАНИЕ ТЕКСТА В БИТЫ ---")
    result = ""
    for i, ch in enumerate(text):
        idx = ALPHABET.index(ch)
        bits = format(idx, '05b')
        print(f"  Буква '{ch}' → индекс {idx:2d} → 5 бит: {bits}")
        result += bits
    print(f"  Итоговая битовая строка: {result}")
    print(f"  Длина: {len(result)} бит")
    return result


def bits_to_text(bits: str) -> str:
    print(f"\n--- ПРЕОБРАЗОВАНИЕ БИТОВ В ТЕКСТ ---")
    chunks = [bits[i:i + 5] for i in range(0, len(bits), 5) if len(bits[i:i + 5]) == 5]
    result = ""
    for i, chunk in enumerate(chunks):
        idx = int(chunk, 2)
        letter = ALPHABET[idx]
        print(f"  Блок {i + 1}: {chunk} (биты) → {idx:2d} (индекс) → буква '{letter}'")
        result += letter
    print(f"  Восстановленный текст: {result}")
    return result


def normalize_text(text: str) -> str:
    print(f"\n--- НОРМАЛИЗАЦИЯ ТЕКСТА ---")
    print(f"  Исходный текст: {text}")
    text = text.lower()
    print(f"  Нижний регистр: {text}")
    text = text.replace('ё', 'е')
    print(f"  Замена ё → е: {text}")

    for punct, repl in PUNCT_MAP.items():
        if punct in text:
            old_text = text
            text = text.replace(punct, repl)
            if old_text != text:
                print(f"  Замена '{punct}' → '{repl}': {text}")

    print(f"  Нормализованный текст: {text}")
    return text


def denormalize_text(text: str) -> str:
    print(f"\n--- ВОССТАНОВЛЕНИЕ ЗНАКОВ ---")
    print(f"  Текст после расшифровки: {text}")

    for word, punct in REV_PUNCT_MAP.items():
        if word in text:
            old_text = text
            text = text.replace(word, punct)
            if old_text != text:
                print(f"  Замена '{word}' → '{punct}': {text}")

    print(f"  Восстановленный текст: {text}")
    return text


# =====================================================================
#   РАБОТА С КЛЮЧОМ И КАДРОМ
# =====================================================================
def get_key_bits() -> str:
    print("\n" + "=" * 70)
    print("ВВОД КЛЮЧА")
    print("=" * 70)

    key_word = input("Ключ (8 русских букв): ").strip().lower()

    invalid = [ch for ch in key_word if ch not in ALPHABET]
    if invalid:
        print(f"Ошибка: недопустимые символы: {invalid}")
        sys.exit(1)

    if len(key_word) < 8:
        print("Ошибка: минимум 8 букв")
        sys.exit(1)

    key_word = key_word[:8]
    print(f"\nКлючевое слово: {key_word}")

    print("\nПреобразование в биты (UTF-8):")
    key_bits = ""
    for i, ch in enumerate(key_word):
        byte = ch.encode('utf-8')
        bits = ''.join(format(b, '08b') for b in byte)
        print(f"  Буква '{ch}' → байт(ы) {list(byte)} → биты: {bits}")
        key_bits += bits

    key_bits = key_bits[:64]
    print(f"\nИтоговый 64-битный ключ: {key_bits}")
    return key_bits


def get_frame_number() -> int:
    try:
        frame = int(input("Номер кадра (по умолчанию 0): ").strip() or "0")
        print(f"  Выбран номер кадра: {frame} (двоичный: {format(frame, '022b')})")
        return frame
    except ValueError:
        print("  Используется номер 0")
        return 0


# =====================================================================
#   ГЕНЕРАТОР A5/1
# =====================================================================
def generate_gamma(key_bits: str, frame_num: int) -> list:
    print(f"\n{'=' * 70}")
    print(f"ГЕНЕРАЦИЯ ГАММЫ ДЛЯ КАДРА {frame_num} (A5/1)")
    print(f"{'=' * 70}")

    r1 = [0] * 19
    r2 = [0] * 22
    r3 = [0] * 23

    print(f"\n1. НАЧАЛЬНОЕ СОСТОЯНИЕ РЕГИСТРОВ:")
    print(f"   R1 (19 бит): {r1}")
    print(f"   R2 (22 бита): {r2}")
    print(f"   R3 (23 бита): {r3}")

    print(f"\n2. ЗАГРУЗКА КЛЮЧА (64 такта):")
    for i in range(64):
        bit = int(key_bits[i])
        
        old_r1 = r1.copy()
        old_r2 = r2.copy()
        old_r3 = r3.copy()

        new_r1 = r1[0] ^ bit
        new_r2 = r2[0] ^ bit
        new_r3 = r3[0] ^ bit

        r1 = r1[1:] + [new_r1]
        r2 = r2[1:] + [new_r2]
        r3 = r3[1:] + [new_r3]

    print(f"\n3. ЗАГРУЗКА НОМЕРА КАДРА (22 такта):")
    frame_bits = format(frame_num, '022b')
    for i in range(22):
        bit = int(frame_bits[i])
        new_r1 = r1[0] ^ bit
        new_r2 = r2[0] ^ bit
        new_r3 = r3[0] ^ bit

        r1 = r1[1:] + [new_r1]
        r2 = r2[1:] + [new_r2]
        r3 = r3[1:] + [new_r3]

    print(f"\n4. ПЕРЕМЕШИВАНИЕ (100 тактов)...")
    for step in range(100):
        maj_sum = r1[8] + r2[10] + r3[10]
        majority = 1 if maj_sum > 1 else 0

        if r1[8] == majority:
            r1 = r1[1:] + [r1[13] ^ r1[16] ^ r1[17] ^ r1[18]]
        else:
            r1 = r1[1:] + [r1[18]]

        if r2[10] == majority:
            r2 = r2[1:] + [r2[20] ^ r2[21]]
        else:
            r2 = r2[1:] + [r2[21]]

        if r3[10] == majority:
            r3 = r3[1:] + [r3[7] ^ r3[20] ^ r3[21] ^ r3[22]]
        else:
            r3 = r3[1:] + [r3[22]]

    print(f"\n5. ГЕНЕРАЦИЯ 114 БИТ ГАММЫ:")
    gamma = []
    for i in range(114):
        maj_sum = r1[8] + r2[10] + r3[10]
        majority = 1 if maj_sum > 1 else 0
        out_bit = r1[18] ^ r2[21] ^ r3[22]
        gamma.append(out_bit)

        if r1[8] == majority:
            r1 = r1[1:] + [r1[13] ^ r1[16] ^ r1[17] ^ r1[18]]
        else:
            r1 = r1[1:] + [r1[18]]

        if r2[10] == majority:
            r2 = r2[1:] + [r2[20] ^ r2[21]]
        else:
            r2 = r2[1:] + [r2[21]]

        if r3[10] == majority:
            r3 = r3[1:] + [r3[7] ^ r3[20] ^ r3[21] ^ r3[22]]
        else:
            r3 = r3[1:] + [r3[22]]

    gamma_str = ''.join(str(bit) for bit in gamma)
    print(f"   Итоговая гамма (первые 30 бит): {gamma_str[:30]}...")
    print(f"   Полная длина гаммы: {len(gamma)} бит")
    return gamma


# =====================================================================
#   ОСНОВНОЙ ШИФРАТОР С ВЫВОДОМ (A5/1)
# =====================================================================
def encrypt_data(data_bits: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПРОЦЕСС ШИФРОВАНИЯ (A5/1)")
    print(f"{'=' * 70}")
    print(f"Исходные данные (биты): {data_bits}")
    print(f"Длина данных: {len(data_bits)} бит")

    result = ""
    frame = start_frame

    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        print(f"\n{'─' * 70}")
        print(f"КАДР {frame}")
        print(f"{'─' * 70}")
        
        gamma = generate_gamma(key_bits, frame)

        print(f"\nПобитовый XOR:")
        xored = ""
        for j in range(len(block)):
            xor = int(block[j]) ^ gamma[j]
            xored += str(xor)
            if j < 10:  
                print(f"  Бит {j + 1:2d}: {block[j]} ⊕ {gamma[j]} = {xor}")

        result += xored
        print(f"\nЗашифрованный блок: {xored}")
        frame += 1

    print(f"\n{'─' * 70}")
    print(f"ИТОГОВЫЙ ЗАШИФРОВАННЫЙ ТЕКСТ (биты): {result}")
    return result


def decrypt_data(cipher_bits: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПРОЦЕСС ДЕШИФРОВАНИЯ (A5/1)")
    print(f"{'=' * 70}")
    return encrypt_data(cipher_bits, key_bits, start_frame)


def encrypt_text(plaintext: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПОЛНЫЙ ЦИКЛ ШИФРОВАНИЯ (A5/1)")
    print(f"{'=' * 70}")

    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data(data_bits, key_bits, start_frame)

    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\n{'=' * 70}")
    print(f"ИТОГОВЫЙ РЕЗУЛЬТАТ (группы по 5 бит):")
    print(formatted)

    return formatted


def decrypt_text(ciphertext: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПОЛНЫЙ ЦИКЛ ДЕШИФРОВАНИЯ (A5/1)")
    print(f"{'=' * 70}")

    bits = ciphertext.replace(' ', '')
    plain_bits = decrypt_data(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)

    print(f"\n{'=' * 70}")
    print(f"ИТОГОВЫЙ РАСШИФРОВАННЫЙ ТЕКСТ:")
    print(final_text)

    return final_text


# =====================================================================
#   ОБЕРТКИ ДЛЯ A5/2 С СОВМЕСТИМЫМ ВЫВОДОМ
# =====================================================================
def encrypt_data_a52(data_bits: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПРОЦЕСС ШИФРОВАНИЯ (A5/2)")
    print(f"{'=' * 70}")
    print(f"Исходные данные (биты): {data_bits}")
    print(f"Длина данных: {len(data_bits)} бит")

    result = ""
    frame = start_frame
    key_list = [int(b) for b in key_bits]

    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        print(f"\n{'─' * 70}")
        print(f"КАДР {frame} (A5/2)")
        print(f"{'─' * 70}")
        print(f"Блок данных ({len(block)} бит): {block}")

        frame_list = [int(b) for b in format(frame, '022b')]
        cipher = A52Cipher()
        cipher.initialize(key_list, frame_list)
        gamma = cipher.generate_keystream(len(block))
        
        gamma_str = ''.join(str(bit) for bit in gamma)
        print(f"\nСгенерирована гамма A5/2 (первые 30 бит): {gamma_str[:30]}...")

        print(f"\nПобитовый XOR:")
        xored = ""
        for j in range(len(block)):
            xor_bit = int(block[j]) ^ gamma[j]
            xored += str(xor_bit)
            if j < 10: 
                print(f"  Бит {j + 1:2d}: {block[j]} ⊕ {gamma[j]} = {xor_bit}")

        result += xored
        print(f"\nЗашифрованный блок: {xored}")
        frame += 1

    print(f"\n{'─' * 70}")
    print(f"ИТОГОВЫЙ ЗАШИФРОВАННЫЙ ТЕКСТ (биты): {result}")
    return result

def decrypt_data_a52(cipher_bits: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПРОЦЕСС ДЕШИФРОВАНИЯ (A5/2)")
    print(f"{'=' * 70}")
    return encrypt_data_a52(cipher_bits, key_bits, start_frame)

def encrypt_text_a52(plaintext: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПОЛНЫЙ ЦИКЛ ШИФРОВАНИЯ (A5/2)")
    print(f"{'=' * 70}")
    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data_a52(data_bits, key_bits, start_frame)
    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\n{'=' * 70}")
    print(f"ИТОГОВЫЙ РЕЗУЛЬТАТ (группы по 5 бит):")
    print(formatted)
    return formatted

def decrypt_text_a52(ciphertext: str, key_bits: str, start_frame: int = 0) -> str:
    print(f"\n{'=' * 70}")
    print("ПОЛНЫЙ ЦИКЛ ДЕШИФРОВАНИЯ (A5/2)")
    print(f"{'=' * 70}")
    bits = ciphertext.replace(' ', '')
    plain_bits = decrypt_data_a52(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)
    print(f"\n{'=' * 70}")
    print(f"ИТОГОВЫЙ РАСШИФРОВАННЫЙ ТЕКСТ:")
    print(final_text)
    return final_text


# =====================================================================
#   ИНТЕРФЕЙС / ГЛАВНОЕ МЕНЮ
# =====================================================================
def main():
    while True:
        print("\n" + "="*50)
        print("ПОТОЧНЫЕ ШИФРЫ A5/1 и A5/2")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        print("="*50)

        choice = input("Выберите пункт меню: ")

        if choice in ['1', '2']:
            # --- Добавлен выбор алгоритма в соответствии с заданием ---
            algo = input("Выберите алгоритм для операции (1 - A5/1, 2 - A5/2): ").strip()
            if algo not in ['1', '2']:
                print("Неверный выбор алгоритма. Возврат в меню.")
                continue

            text = input("Введите текст: ").strip()
            key_bits = get_key_bits()
            frame_num = get_frame_number()
            
            if choice == '1':
                if algo == '1':
                    encrypt_text(text, key_bits, frame_num)
                else:
                    encrypt_text_a52(text, key_bits, frame_num)
            elif choice == '2':
                if algo == '1':
                    decrypt_text(text, key_bits, frame_num)
                else:
                    decrypt_text_a52(text, key_bits, frame_num)
                
        elif choice == '3':
            print("Работа завершена. До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")
            continue

        cont = input("\nПродолжить выполнение всей программы? (да/нет): ").lower()
        if cont not in ['да', 'д', 'yes', 'y']:
            print("Работа завершена.")
            break

if __name__ == "__main__":
    main()