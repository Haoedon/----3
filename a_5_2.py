import hashlib
import os
from punctuation import convert_punctuation
from text_preprocessor import preprocess_text

ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 
            'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 
            'ы', 'ь', 'э', 'ю', 'я']

PUNCT_WORDS = ['тчк', 'зпт', 'впр', 'вск', 'двтч', 'тчзпт', 'тире', 'скоб', 'скобз', 'квч', 'апстр', 'прб']
PUNCT_SYMBOLS = ['.', ',', '?', '!', ':', ';', '-', '(', ')', '"', "'", ' ']

PUNCT_WORD_TO_SYMBOL = dict(zip(PUNCT_WORDS, PUNCT_SYMBOLS))
PUNCT_SYMBOL_TO_WORD = dict(zip(PUNCT_SYMBOLS, PUNCT_WORDS))

CHAR_TO_CODE = {char: i for i, char in enumerate(ALPHABET)}
CODE_TO_CHAR = {i: char for i, char in enumerate(ALPHABET)}

OUTPUT_DIR = "lab6"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def majority(x, y, z):
    return (x & y) | (x & z) | (y & z)

class A5_2:
    def __init__(self, key_bits, frame_bits):
        self.R1 = [0] * 19
        self.R2 = [0] * 22
        self.R3 = [0] * 23

        self.key_bits = key_bits
        self.frame_bits = frame_bits

        self.initialize()

    def clock(self, bit=0):
        m = majority(self.R1[8], self.R2[10], self.R3[10])

        fb1 = self.R1[13] ^ self.R1[16] ^ self.R1[17] ^ self.R1[18] ^ bit ^ m ^ 1
        fb2 = self.R2[20] ^ self.R2[21] ^ bit ^ m
        fb3 = self.R3[7] ^ self.R3[20] ^ self.R3[21] ^ self.R3[22] ^ bit ^ m

        self.R1 = [fb1] + self.R1[:-1]
        self.R2 = [fb2] + self.R2[:-1]
        self.R3 = [fb3] + self.R3[:-1]

    def initialize(self):
        for b in self.key_bits:
            self.clock(int(b))

        for b in self.frame_bits:
            self.clock(int(b))

        for _ in range(99):
            self.clock()

    def keystream_bit(self):
        self.clock()
        return self.R1[18] ^ self.R2[21] ^ self.R3[22]

    def keystream(self, n):
        return [self.keystream_bit() for _ in range(n)]

def password_to_key(password: str) -> list[int]:
    hash_bytes = hashlib.sha256(password.encode("utf-8")).digest()
    key_bits = []
    for byte in hash_bytes[:8]:
        key_bits.extend(int(b) for b in format(byte, "08b"))
    return key_bits


def format_key_bits(key_bits):
    result = ""
    for i in range(0, len(key_bits), 8):
        if i + 8 <= len(key_bits):
            byte = key_bits[i:i+8]
            byte_str = ''.join(map(str, byte))
            result += byte_str + " "
    return result.strip()


def frame_to_bits(frame_str: str) -> list[int]:
    return [int(bit) for bit in frame_str]

def text_to_punct_words(text):
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in PUNCT_SYMBOL_TO_WORD:
            result.append(PUNCT_SYMBOL_TO_WORD[char])
        else:
            result.append(char)
        i += 1
    return ''.join(result)


def punct_words_to_text(text_with_punct):
    result = []
    i = 0
    text_lower = text_with_punct.lower()
    
    while i < len(text_lower):
        # Проверяем все возможные слова-знаки (сначала более длинные)
        matched = False
        for punct_word in sorted(PUNCT_WORDS, key=len, reverse=True):
            if text_lower[i:].startswith(punct_word):
                # Нашли слово-знак
                result.append(PUNCT_WORD_TO_SYMBOL[punct_word])
                i += len(punct_word)
                matched = True
                break
        
        if not matched:
            # Обычный символ
            result.append(text_with_punct[i])
            i += 1
    
    return ''.join(result)


def text_to_5bit_codes(text):
    # Сначала заменяем знаки препинания и пробелы на слова
    text_with_punct_words = text_to_punct_words(text)
    
    # Приводим к нижнему регистру для соответствия алфавиту
    text_lower = text_with_punct_words.lower()
    
    codes = []
    processed_chars = []
    
    # Кодируем каждый символ
    for char in text_lower:
        if char in CHAR_TO_CODE:
            codes.append(CHAR_TO_CODE[char])
            processed_chars.append(char)
        else:
            # Если символа нет в алфавите, заменяем на 'а'
            codes.append(0)
            processed_chars.append('а')
    
    processed_text = ''.join(processed_chars)
    return codes, processed_text, text_with_punct_words


def codes_to_text(codes):
    # Сначала преобразуем коды в символы
    chars = []
    for code in codes:
        if 0 <= code < len(ALPHABET):
            chars.append(ALPHABET[code])
        else:
            chars.append('а')

    text_with_punct_words = ''.join(chars)

    final_text = punct_words_to_text(text_with_punct_words)
    
    return final_text


def codes_to_bits(codes):
    bits = []
    for code in codes:
        bits.extend(int(b) for b in format(code, '05b'))
    return bits


def bits_to_codes(bits):
    codes = []
    for i in range(0, len(bits), 5):
        if i + 5 <= len(bits):
            code_bits = bits[i:i+5]
            code = int(''.join(map(str, code_bits)), 2)
            codes.append(code)
    return codes


def xor_bits(a, b):
    return [x ^ y for x, y in zip(a, b)]


def get_file_path(filename):
    ensure_output_dir()
    return os.path.join(OUTPUT_DIR, filename)


def save_to_file(filename, content):
    filepath = get_file_path(filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def load_from_file(filename):
    filepath = get_file_path(filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def print_progress(current, total, prefix="Прогресс"):
    if total > 1000:
        percent = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f'\r{prefix}: |{bar}| {percent:.1f}% ({current}/{total})', end='', flush=True)
        if current == total:
            print()


def verify_decryption(original_text, decrypted_text):
    if original_text and decrypted_text:
        if original_text == decrypted_text:
            print("\n✅ РАСШИФРОВКА УСПЕШНА!")
            return True
        else:
            print("\n⚠️ РАСШИФРОВКА НЕ УДАЛАСЬ")
            min_len = min(len(original_text), len(decrypted_text))
            for i in range(min_len):
                if original_text[i] != decrypted_text[i]:
                    print(f"Первое несовпадение на позиции {i}:")
                    start = max(0, i-20)
                    end = min(len(original_text), i+20)
                    print(f"Оригинал: {original_text[start:end]}")
                    print(f"Расшифр: {decrypted_text[start:end]}")
                    break
            return False
    return False

def main():
    ensure_output_dir() 
    original_text = None
    
    while True:
        print("\n=== A5/2 (5 бит на символ) ===")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Показать список файлов")
        print("0. Выход")

        choice = input("> ")

        if choice == "0":
            break
            
        elif choice == "3":
            print(f"\n📂 Файлы в директории {OUTPUT_DIR}:")
            try:
                files = os.listdir(OUTPUT_DIR)
                if files:
                    for file in sorted(files):
                        filepath = os.path.join(OUTPUT_DIR, file)
                        size = os.path.getsize(filepath)
                        print(f"   - {file} ({size} байт)")
                else:
                    print("   Директория пуста")
            except FileNotFoundError:
                print("   Директория не найдена")
            continue

        key_input = input("Введите пароль или 64 бита ключа: ")
        
        if len(key_input) == 64 and all(bit in '01' for bit in key_input):
            key_bits = [int(bit) for bit in key_input]
            print("🔑 Используется прямой 64-битный ключ")
        else:
            key_bits = password_to_key(key_input)
            print(f"🔑 Пароль преобразован в ключ: {format_key_bits(key_bits)}")
        
        frame_str = input("Введите номер кадра (22 бита): ")
        
        if len(frame_str) != 22 or not all(bit in '01' for bit in frame_str):
            print("❌ Номер кадра должен содержать 22 бита (только 0 и 1)!")
            continue

        frame_bits = frame_to_bits(frame_str)
        
        print(f"📡 Номер кадра: {frame_str}")

        if choice == "1":
            print("\nВведите открытый текст:")
            print("(Для завершения ввода нажмите Ctrl+Z (Windows) или Ctrl+D (Linux) затем Enter)")
            try:
                lines = []
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                text = '\n'.join(lines)
            
            if not text:
                print("❌ Текст не введен")
                continue
            
            original_text = text
            
            print(f"\n📝 Обработка текста длиной {len(text)} символов...")
            
            print("\n📋 Пример преобразования знаков препинания:")
            example_text = text[:100] + "..." if len(text) > 100 else text
            example_converted = text_to_punct_words(example_text)
            print(f"   Исходный: {example_text}")
            print(f"   После замены: {example_converted}")
            
            codes, processed_text, text_with_punct = text_to_5bit_codes(text)
            chars_count = len(codes)
            print(f"\n📊 Количество символов после обработки: {chars_count}")
            print(f"📊 Текст со вставленными словами-знаками: {text_with_punct[:200]}...")
            
            bits = codes_to_bits(codes)
            bits_count = len(bits)
            print(f"📏 Всего бит для шифрования: {bits_count}")
            
            print("\n🔐 Процесс шифрования...")
            cipher = A5_2(key_bits, frame_bits)
            
            chunk_size = 10000
            cipher_bits = []
            
            for i in range(0, bits_count, chunk_size):
                end = min(i + chunk_size, bits_count)
                chunk_plain = bits[i:end]
                gamma = cipher.keystream(len(chunk_plain))
                chunk_cipher = xor_bits(chunk_plain, gamma)
                cipher_bits.extend(chunk_cipher)
                print_progress(end, bits_count, "Шифрование")
            
            cipher_text = "".join(map(str, cipher_bits))
            cipher_file = save_to_file("cipher_text_A5_2.txt", cipher_text)

            info_content = f"""=== ИНФОРМАЦИЯ О ШИФРОВАНИИ (A5/2) ===
Ключ (64 бита): {format_key_bits(key_bits)}
Номер кадра: {frame_str}
Количество символов: {chars_count}
Количество бит: {bits_count}

ИСХОДНЫЙ ТЕКСТ:
{text}

ТЕКСТ СО ВСТАВЛЕННЫМИ СЛОВАМИ-ЗНАКАМИ:
{text_with_punct}

5-БИТНЫЕ КОДЫ:
{codes}
"""
            info_file = save_to_file("cipher_info_A5_2.txt", info_content)

            print(f"\n✔ Шифротекст сохранён: {cipher_file}")
            print(f"✔ Информация сохранена: {info_file}")

        elif choice == "2":
            filename = input("\nВведите имя файла с шифротекстом (в lab6/): ")
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            try:
                cipher_text = load_from_file(filename)
                cipher_bits = [int(bit) for bit in cipher_text.strip() if bit in '01']
                bits_count = len(cipher_bits)
                print(f"📖 Загружено {bits_count} бит из файла: {filename}")
                print(f"Первые 50 бит: {''.join(map(str, cipher_bits[:50]))}...")
                
            except FileNotFoundError:
                print(f"❌ Файл {filename} не найден")
                continue
            except ValueError as e:
                print(f"❌ Ошибка чтения файла: {e}")
                continue

            print("\n🔓 Процесс расшифровки...")
            cipher = A5_2(key_bits, frame_bits)
            
            chunk_size = 10000
            plain_bits = []
            
            for i in range(0, bits_count, chunk_size):
                end = min(i + chunk_size, bits_count)
                chunk_cipher = cipher_bits[i:end]
                gamma = cipher.keystream(len(chunk_cipher))
                chunk_plain = xor_bits(chunk_cipher, gamma)
                plain_bits.extend(chunk_plain)
                print_progress(end, bits_count, "Расшифровка")

            codes = bits_to_codes(plain_bits)
            print(f"\n📊 Восстановлено кодов: {len(codes)}")
            print(f"📊 Первые 20 кодов: {codes[:20]}...")
            
            text_with_punct = codes_to_text(codes)
            
            print(f"\n📝 Текст после расшифровки (со словами-знаками):")
            print(f"{text_with_punct[:200]}...")

            decrypted_file = save_to_file("decrypted_text_A5_2.txt", text_with_punct)
            
            info_content = f"""=== ИНФОРМАЦИЯ О РАСШИФРОВАНИИ (A5/2) ===
Ключ (64 бита): {format_key_bits(key_bits)}
Номер кадра: {frame_str}
Исходный файл: {filename}
Количество бит: {bits_count}
Количество символов: {len(codes)}
5-битные коды: {codes}

РАСШИФРОВАННЫЙ ТЕКСТ:
{text_with_punct}
"""
            info_file = save_to_file("decrypt_info_A5_2.txt", info_content)

            print(f"\n✔ Расшифрованный текст сохранён: {decrypted_file}")
            print(f"✔ Информация сохранена: {info_file}")
            
            print(f"\n📝 ИТОГОВЫЙ РАСШИФРОВАННЫЙ ТЕКСТ:")
            print(text_with_punct[:500] + ("..." if len(text_with_punct) > 500 else ""))
            
            if original_text:
                verify_decryption(original_text, text_with_punct)


if __name__ == "__main__":
    main()