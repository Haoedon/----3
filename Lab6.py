import sys
from itertools import zip_longest

# =====================================================================
#   КОНСТАНТЫ
# =====================================================================
# Алфавит для кодирования (32 символа, что позволяет использовать 5 бит на символ)
ALPHABET = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
            "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
            "ъ", "ы", "ь", "э", "ю", "я"]

# Словарь для замены знаков препинания на текстовые коды (нормализация)
PUNCT_MAP = {
    '.': 'тчк', ',': 'зпт', ';': 'тчз', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз', "'": 'апстр', ' ': 'прбл'
}
# Обратный словарь для восстановления знаков препинания
REV_PUNCT_MAP = {v: k for k, v in PUNCT_MAP.items()}


# =====================================================================
#   КЛАСС АЛГОРИТМА A5/2
# =====================================================================
class A52Cipher:
    """Реализация логики поточного шифра A5/2 с четырьмя регистрами."""

    def __init__(self):
        """Инициализация четырех регистров R1, R2, R3 и управляющего R4 нулевыми битами."""
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23
        self.R4 = [0] * 17

    def majority(self, x, y, z):
        """
        Вычисляет мажоритарное значение (какой бит встречается чаще: 0 или 1).
        Используется для управления движением регистров.
        """
        return (x & y) | (x & z) | (y & z)

    def clock_all(self, input_bit):
        """
        Принудительный сдвиг всех четырех регистров.
        Используется на этапах загрузки секретного ключа и номера кадра.
        """
        # Вычисление битов обратной связи по полиномам для каждого регистра
        nb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18] ^ input_bit
        nb2 = self.R2[20] ^ self.R2[21] ^ input_bit
        nb3 = self.R3[7]  ^ self.R3[20] ^ self.R3[21] ^ self.R3[22] ^ input_bit
        nb4 = self.R4[11] ^ self.R4[16] ^ input_bit

        # Сдвиг и вставка нового бита в начало
        self.R1 = [nb1] + self.R1[:-1]
        self.R2 = [nb2] + self.R2[:-1]
        self.R3 = [nb3] + self.R3[:-1]
        self.R4 = [nb4] + self.R4[:-1]

    def clock_stop_go(self, generate_output=False):
        """
        Условный сдвиг регистров на основе состояния управляющего регистра R4.
        Если generate_output=True, возвращает один бит сформированной гаммы.
        """
        # Мажоритарная функция по битам R4
        f = self.majority(self.R4[3], self.R4[7], self.R4[10])

        # Определение, какие регистры (R1, R2, R3) должны сдвинуться
        shift_r1 = (self.R4[10] == f)
        shift_r2 = (self.R4[3]  == f)
        shift_r3 = (self.R4[7]  == f)

        # R4 всегда сдвигается
        nb4 = self.R4[11] ^ self.R4[16]
        self.R4 = [nb4] + self.R4[:-1]

        # Сдвиг выбранных регистров
        if shift_r1:
            nb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18]
            self.R1 = [nb1] + self.R1[:-1]
        if shift_r2:
            nb2 = self.R2[20] ^ self.R2[21]
            self.R2 = [nb2] + self.R2[:-1]
        if shift_r3:
            nb3 = self.R3[7] ^ self.R3[20] ^ self.R3[21] ^ self.R3[22]
            self.R3 = [nb3] + self.R3[:-1]

        # Генерация выходного бита гаммы путем XOR выходов и мажоритарных функций внутренних битов
        if generate_output:
            out = self.R1[18] ^ self.R2[21] ^ self.R3[22]
            maj1 = self.majority(self.R1[12], self.R1[14], self.R1[15])
            maj2 = self.majority(self.R2[9],  self.R2[13], self.R2[16])
            maj3 = self.majority(self.R3[13], self.R3[16], self.R3[18])
            return out ^ maj1 ^ maj2 ^ maj3
        return None

    def initialize(self, key_bits, frame_bits):
        """
        Полный цикл инициализации состояния шифра:
        1. Обнуление. 2. Загрузка ключа. 3. Загрузка кадра. 4. 100 тактов перемешивания.
        """
        self.R1 = [0]*19
        self.R2 = [0]*22
        self.R3 = [0]*23
        self.R4 = [0]*17

        for b in key_bits:
            self.clock_all(b)

        for b in frame_bits:
            self.clock_all(b)

        # Установка битов в R4 для предотвращения нулевого состояния
        self.R4[3] = 1
        self.R4[7] = 1
        self.R4[10] = 1

        for _ in range(64):
            self.clock_stop_go(generate_output=False)

    def generate_keystream(self, length):
        """Генерирует последовательность битов гаммы заданной длины."""
        ks = []
        for _ in range(length):
            ks.append(self.clock_stop_go(generate_output=True))
        return ks


# =====================================================================
#   ПРЕОБРАЗОВАНИЕ ТЕКСТА
# =====================================================================
def text_to_bits(text: str) -> str:
    """
    Конвертирует строку текста в битовую строку.
    Каждый символ алфавита заменяется его 5-битным индексом.
    """
    print(f"\n--- ПРЕОБРАЗОВАНИЕ ТЕКСТА В БИТЫ ---")
    result = ""
    for i, ch in enumerate(text):
        idx = ALPHABET.index(ch)
        bits = format(idx, '05b')
        print(f"  Буква '{ch}' → индекс {idx:2d} → 5 бит: {bits}")
        result += bits
    print(f"  Итоговая битовая строка: {result}")
    return result


def bits_to_text(bits: str) -> str:
    """
    Конвертирует битовую строку обратно в текст.
    Берет каждые 5 бит, переводит в число и находит букву в ALPHABET.
    """
    print(f"\n--- ПРЕОБРАЗОВАНИЕ БИТОВ В ТЕКСТ ---")
    chunks = [bits[i:i + 5] for i in range(0, len(bits), 5) if len(bits[i:i + 5]) == 5]
    result = ""
    for i, chunk in enumerate(chunks):
        idx = int(chunk, 2)
        letter = ALPHABET[idx]
        print(f"  Блок {i + 1}: {chunk} (биты) → {idx:2d} (индекс) → буква '{letter}'")
        result += letter
    return result


def normalize_text(text: str) -> str:
    """
    Подготовка текста к шифрованию: приведение к нижнему регистру,
    замена 'ё' на 'е' и замена знаков препинания на их буквенные коды.
    """
    print(f"\n--- НОРМАЛИЗАЦИЯ ТЕКСТА ---")
    text = text.lower().replace('ё', 'е')
    for punct, repl in PUNCT_MAP.items():
        text = text.replace(punct, repl)
    print(f"  Результат: {text}")
    return text


def denormalize_text(text: str) -> str:
    """
    Восстановление исходного вида текста: замена буквенных кодов (тчк, зпт)
    обратно на знаки препинания.
    """
    print(f"\n--- ВОССТАНОВЛЕНИЕ ЗНАКОВ ---")
    for word, punct in REV_PUNCT_MAP.items():
        text = text.replace(word, punct)
    print(f"  Результат: {text}")
    return text


# =====================================================================
#   РАБОТА С КЛЮЧОМ И КАДРОМ
# =====================================================================
def get_key_bits() -> str:
    """
    Запрашивает у пользователя ключ (8 букв) и преобразует его
    в 64-битную последовательность (через UTF-8 байты).
    """
    print("\n" + "=" * 70 + "\nВВОД КЛЮЧА\n" + "=" * 70)
    key_word = input("Ключ (8 русских букв): ").strip().lower()
    
    if len(key_word) < 8:
        print("Ошибка: минимум 8 букв")
        sys.exit(1)

    key_word = key_word[:8]
    key_bits = ""
    for ch in key_word:
        byte = ch.encode('utf-8')
        # Берем только значащие биты для формирования ключа
        bits = ''.join(format(b, '08b') for b in byte)
        key_bits += bits

    # Обрезаем до стандартных 64 бит
    final_key = key_bits[:64]
    print(f"Итоговый 64-битный ключ: {final_key}")
    return final_key


def get_frame_number() -> int:
    """Запрашивает у пользователя номер кадра для инициализации шифра."""
    try:
        frame = int(input("Номер кадра (по умолчанию 0): ").strip() or "0")
        return frame
    except ValueError:
        return 0


# =====================================================================
#   АЛГОРИТМ A5/1 (ЛОГИКА ИЗ Lab6.py)
# =====================================================================
def generate_gamma(key_bits: str, frame_num: int) -> list:
    """
    Реализация формирования 114 бит гаммы по алгоритму A5/1.
    Включает фазы загрузки ключа, номера кадра и перемешивания.
    """
    print(f"\nГЕНЕРАЦИЯ ГАММЫ (A5/1) ДЛЯ КАДРА {frame_num}")
    
    # Инициализация регистров A5/1
    r1, r2, r3 = [0]*19, [0]*22, [0]*23

    # Загрузка 64 бит ключа
    for i in range(64):
        bit = int(key_bits[i])
        r1 = r1[1:] + [r1[0] ^ bit]
        r2 = r2[1:] + [r2[0] ^ bit]
        r3 = r3[1:] + [r3[0] ^ bit]

    # Загрузка 22 бит номера кадра
    frame_bits = format(frame_num, '022b')
    for i in range(22):
        bit = int(frame_bits[i])
        r1 = r1[1:] + [r1[0] ^ bit]
        r2 = r2[1:] + [r2[0] ^ bit]
        r3 = r3[1:] + [r3[0] ^ bit]

    # 100 тактов перемешивания с мажоритарным управлением
    for _ in range(100):
        maj = 1 if (r1[8] + r2[10] + r3[10]) > 1 else 0
        if r1[8] == maj: r1 = r1[1:] + [r1[13]^r1[16]^r1[17]^r1[18]]
        else: r1 = r1[1:] + [r1[18]]
        if r2[10] == maj: r2 = r2[1:] + [r2[20]^r2[21]]
        else: r2 = r2[1:] + [r2[21]]
        if r3[10] == maj: r3 = r3[1:] + [r3[7]^r3[20]^r3[21]^r3[22]]
        else: r3 = r3[1:] + [r3[22]]

    # Генерация выходных бит
    gamma = []
    for _ in range(114):
        maj = 1 if (r1[8] + r2[10] + r3[10]) > 1 else 0
        gamma.append(r1[18] ^ r2[21] ^ r3[22])
        # Сдвиг...
        if r1[8] == maj: r1 = r1[1:] + [r1[13]^r1[16]^r1[17]^r1[18]]
        else: r1 = r1[1:] + [r1[18]]
        if r2[10] == maj: r2 = r2[1:] + [r2[20]^r2[21]]
        else: r2 = r2[1:] + [r2[21]]
        if r3[10] == maj: r3 = r3[1:] + [r3[7]^r3[20]^r3[21]^r3[22]]
        else: r3 = r3[1:] + [r3[22]]

    return gamma


def encrypt_data(data_bits: str, key_bits: str, start_frame: int = 0) -> str:
    """Шифрование битов данных алгоритмом A5/1 путем поблочного XOR с гаммой."""
    result = ""
    frame = start_frame
    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        gamma = generate_gamma(key_bits, frame)
        xored = "".join(str(int(block[j]) ^ gamma[j]) for j in range(len(block)))
        result += xored
        frame += 1
    return result


def decrypt_data(cipher_bits: str, key_bits: str, start_frame: int = 0) -> str:
    """Расшифрование A5/1 (идентично шифрованию для поточных шифров)."""
    return encrypt_data(cipher_bits, key_bits, start_frame)


def encrypt_text(plaintext: str, key_bits: str, start_frame: int = 0) -> str:
    """Верхнеуровневая функция: текст -> нормализация -> биты -> A5/1 -> результат."""
    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data(data_bits, key_bits, start_frame)
    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\nИТОГОВЫЙ РЕЗУЛЬТАТ (A5/1): {formatted}")
    return formatted


def decrypt_text(ciphertext: str, key_bits: str, start_frame: int = 0) -> str:
    """Верхнеуровневая функция: биты -> A5/1 -> биты -> текст -> денормализация."""
    bits = ciphertext.replace(' ', '')
    plain_bits = decrypt_data(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)
    print(f"\nИТОГОВЫЙ ТЕКСТ (A5/1): {final_text}")
    return final_text


# =====================================================================
#   АЛГОРИТМ A5/2 (ОБЕРТКИ)
# =====================================================================
def encrypt_data_a52(data_bits: str, key_bits: str, start_frame: int = 0) -> str:
    """Шифрование битов данных с использованием класса A52Cipher."""
    result = ""
    frame = start_frame
    key_list = [int(b) for b in key_bits]
    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        frame_list = [int(b) for b in format(frame, '022b')]
        cipher = A52Cipher()
        cipher.initialize(key_list, frame_list)
        gamma = cipher.generate_keystream(len(block))
        xored = "".join(str(int(block[j]) ^ gamma[j]) for j in range(len(block)))
        result += xored
        frame += 1
    return result


def decrypt_data_a52(cipher_bits: str, key_bits: str, start_frame: int = 0) -> str:
    
    
    return encrypt_data_a52(cipher_bits, key_bits, start_frame)


def encrypt_text_a52(plaintext: str, key_bits: str, start_frame: int = 0) -> str:
    """Полный цикл шифрования текста через алгоритм A5/2."""
    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data_a52(data_bits, key_bits, start_frame)
    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\nИТОГОВЫЙ РЕЗУЛЬТАТ (A5/2): {formatted}")
    return formatted


def decrypt_text_a52(ciphertext: str, key_bits: str, start_frame: int = 0) -> str:
    
    bits = ciphertext.replace(' ', '')
    plain_bits = decrypt_data_a52(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)
    print(f"\nИТОГОВЫЙ ТЕКСТ (A5/2): {final_text}")
    return final_text


# =====================================================================
#   ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ
# =====================================================================
def main():
   
    while True:
        print("\n" + "="*50)
        print("ПОТОЧНЫЙ ШИФР A5 (A5/1 и A5/2)")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        print("="*50)

        choice = input("Выберите пункт меню: ")

        if choice in ['1', '2']:
            algo = input("Выберите алгоритм (1 - A5/1, 2 - A5/2): ").strip()
            if algo not in ['1', '2']:
                print("Ошибка выбора.")
                continue


            text = input("Введите текст или биты : ").strip()

           

            key_bits = get_key_bits()
            frame_num = get_frame_number()
            
            if choice == '1':
                if algo == '1': encrypt_text(text, key_bits, frame_num)
                else: encrypt_text_a52(text, key_bits, frame_num)
            elif choice == '2':
                if algo == '1': decrypt_text(text, key_bits, frame_num)
                else: decrypt_text_a52(text, key_bits, frame_num)
                
        elif choice == '3':
            print("Выход из программы.")
            break

        if input("\nПродолжить? (да/нет): ").lower() not in ['да', 'д', 'y']:
            break

if __name__ == "__main__":
    main()