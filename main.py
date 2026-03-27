"""
ПРОГРАММА ШИФРОВАНИЯ ТЕКСТА - МНОГОЗНАЧНАЯ ЗАМЕНА

Реализация всех методов в одном файле:
1. Шифр Виженера (ключевое слово) - классический вариант
2. Шифр Виженера (самоключ) - открытый текст расширяет ключ
3. Шифр Тритемия - прогрессивный сдвиг
4. Шифр Белазо - с перестановкой алфавита
5. S-блок ГОСТ Р 34.12-2015 - блочный шифр

Все функции и классы используют русский алфавит (33 буквы)
и обрабатывают пунктуацию согласно заданному формату
"""


# ============================================================================
# РЕАЛИЗАЦИЯ ШИФРОВ МНОГОЗНАЧНОЙ ЗАМЕНЫ
# ============================================================================

class VigenereCipher:
    """Шифр Виженера (вариант с ключевым словом) - многозначная замена"""
    
    def __init__(self, key: str):
        """
        Инициализация шифра Виженера с ключевым словом
        :param key: ключевое слово для шифрования
        """
        self.key = key.upper().replace('Ё', 'Е')
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста (ключевое слово циклически повторяется)
        :param plaintext: исходный текст
        :return: зашифрованный текст
        """
        plaintext = plaintext.upper().replace('Ё', 'Е')
        ciphertext = ''
        key_index = 0
        
        for char in plaintext:
            if char in self.alphabet:
                char_index = self.alphabet.index(char)
                key_char = self.key[key_index % len(self.key)]
                key_index_in_alphabet = self.alphabet.index(key_char)
                encrypted_index = (char_index + key_index_in_alphabet) % self.alphabet_size
                ciphertext += self.alphabet[encrypted_index]
                key_index += 1
            else:
                ciphertext += char
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровка текста
        :param ciphertext: зашифрованный текст
        :return: исходный текст
        """
        ciphertext = ciphertext.upper().replace('Ё', 'Е')
        plaintext = ''
        key_index = 0
        
        for char in ciphertext:
            if char in self.alphabet:
                char_index = self.alphabet.index(char)
                key_char = self.key[key_index % len(self.key)]
                key_index_in_alphabet = self.alphabet.index(key_char)
                decrypted_index = (char_index - key_index_in_alphabet) % self.alphabet_size
                plaintext += self.alphabet[decrypted_index]
                key_index += 1
            else:
                plaintext += char
        
        return plaintext


class VigenereAutokeyCipher:
    """Шифр Виженера (вариант самоключ) - открытый текст расширяет ключ"""
    
    def __init__(self, key: str):
        """
        Инициализация шифра Виженера с самоключом
        :param key: начальный ключ
        """
        self.initial_key = key.upper().replace('Ё', 'Е')
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста (открытый текст служит продолжением ключа)
        :param plaintext: исходный текст
        :return: зашифрованный текст
        
        Алгоритм:
        - Ключ начинается с исходного ключа
        - После него добавляются буквы открытого текста
        - Каждая буква текста сдвигается на соответствующую букву ключа
        """
        plaintext = plaintext.upper().replace('Ё', 'Е')
        ciphertext = ''
        
        # Расширенный ключ: начальный ключ + открытый текст (только буквы)
        extended_key = self.initial_key + ''.join(c for c in plaintext if c in self.alphabet)
        
        letter_index = 0  # Индекс для букв открытого текста
        
        for char in plaintext:
            if char in self.alphabet:
                char_index = self.alphabet.index(char)
                key_char = extended_key[letter_index]
                key_index_in_alphabet = self.alphabet.index(key_char)
                encrypted_index = (char_index + key_index_in_alphabet) % self.alphabet_size
                ciphertext += self.alphabet[encrypted_index]
                letter_index += 1
            else:
                ciphertext += char
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровка текста
        :param ciphertext: зашифрованный текст
        :return: исходный текст
        
        Процесс:
        - Ключ начинается с исходного ключа
        - Каждую букву шифротекста расшифровываем, получаем открытый текст
        - Полученную букву добавляем в расширенный ключ
        """
        ciphertext = ciphertext.upper().replace('Ё', 'Е')
        plaintext = ''
        
        extended_key = self.initial_key
        letter_index = 0
        
        for char in ciphertext:
            if char in self.alphabet:
                char_index = self.alphabet.index(char)
                key_char = extended_key[letter_index]
                key_index_in_alphabet = self.alphabet.index(key_char)
                decrypted_index = (char_index - key_index_in_alphabet) % self.alphabet_size
                decrypted_char = self.alphabet[decrypted_index]
                plaintext += decrypted_char
                
                # Добавляем расшифрованного символа в расширенный ключ
                extended_key += decrypted_char
                letter_index += 1
            else:
                plaintext += char
        
        return plaintext


class TrithemiusCipher:
    """Шифр Тритемия - прогрессивный шифр многозначной замены"""
    
    def __init__(self, initial_shift: int = 0):
        """
        Инициализация шифра Тритемия
        :param initial_shift: начальный сдвиг
        """
        self.initial_shift = initial_shift
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста с прогрессивным сдвигом
        :param plaintext: исходный текст
        :return: зашифрованный текст
        """
        plaintext = plaintext.upper().replace('Ё', 'Е')
        ciphertext = ''
        shift = self.initial_shift
        
        for char in plaintext:
            if char in self.alphabet:
                char_index = self.alphabet.index(char)
                encrypted_index = (char_index + shift) % self.alphabet_size
                ciphertext += self.alphabet[encrypted_index]
                shift += 1
            else:
                ciphertext += char
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровка текста
        :param ciphertext: зашифрованный текст
        :return: исходный текст
        """
        ciphertext = ciphertext.upper().replace('Ё', 'Е')
        plaintext = ''
        shift = self.initial_shift
        
        for char in ciphertext:
            if char in self.alphabet:
                char_index = self.alphabet.index(char)
                decrypted_index = (char_index - shift) % self.alphabet_size
                plaintext += self.alphabet[decrypted_index]
                shift += 1
            else:
                plaintext += char
        
        return plaintext


class BelasoCipher:
    """Шифр Белазо - многозначная замена с перестановкой алфавита"""
    
    def __init__(self, key: str):
        """
        Инициализация шифра Белазо
        :param key: секретный ключ
        """
        self.key = key.upper().replace('Ё', 'Е')
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def _create_alphabet_permutation(self, shift: int) -> str:
        """
        Создает перестановленный алфавит со сдвигом
        :param shift: величина сдвига
        :return: перестановленный алфавит
        """
        return self.alphabet[(shift % self.alphabet_size):] + self.alphabet[:(shift % self.alphabet_size)]
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста
        :param plaintext: исходный текст
        :return: зашифрованный текст
        """
        plaintext = plaintext.upper().replace('Ё', 'Е')
        ciphertext = ''
        key_index = 0
        
        for char in plaintext:
            if char in self.alphabet:
                key_char = self.key[key_index % len(self.key)]
                shift = self.alphabet.index(key_char)
                shifted_alphabet = self._create_alphabet_permutation(shift)
                char_index = self.alphabet.index(char)
                ciphertext += shifted_alphabet[char_index]
                key_index += 1
            else:
                ciphertext += char
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровка текста
        :param ciphertext: зашифрованный текст
        :return: исходный текст
        """
        ciphertext = ciphertext.upper().replace('Ё', 'Е')
        plaintext = ''
        key_index = 0
        
        for char in ciphertext:
            if char in self.alphabet:
                key_char = self.key[key_index % len(self.key)]
                shift = self.alphabet.index(key_char)
                shifted_alphabet = self._create_alphabet_permutation(shift)
                char_index = shifted_alphabet.index(char)
                plaintext += self.alphabet[char_index]
                key_index += 1
            else:
                plaintext += char
        
        return plaintext


class GOSTCipher:
    """S-блок замены ГОСТ Р 34.12-2015 (упрощенная реализация)"""
    
    SBOX = [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 0, 5],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 15, 3, 12, 2],
        [13, 8, 15, 1, 2, 5, 4, 14, 7, 0, 10, 12, 6, 9, 3, 11],
    ]
    
    def __init__(self, key: str):
        """
        Инициализация ГОСТ шифра
        :param key: ключ шифрования
        """
        self.key = key.upper().replace('Ё', 'Е')
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def _apply_sbox(self, byte_val: int, sbox_num: int) -> int:
        """Применение S-блока к 4-битному значению"""
        if sbox_num >= len(self.SBOX):
            sbox_num = sbox_num % len(self.SBOX)
        return self.SBOX[sbox_num][byte_val & 0x0F]
    
    def _create_round_key(self, round_num: int) -> list:
        """Создает раундовый ключ"""
        key_bytes = []
        for char in self.key:
            char_index = self.alphabet.index(char)
            key_bytes.append(char_index)
        
        round_key = []
        for i in range(8):
            key_index = (i + round_num) % len(key_bytes)
            round_key.append(key_bytes[key_index])
        
        return round_key
    
    def _feistel_round(self, left: int, right: int, round_key: list) -> tuple:
        """Раунд сети Фейстеля"""
        f_result = right ^ round_key[0]
        
        for i in range(4):
            nibble = (f_result >> (i * 8)) & 0xFF
            s1 = self._apply_sbox((nibble >> 4) & 0x0F, i * 2)
            s2 = self._apply_sbox(nibble & 0x0F, i * 2 + 1)
            f_result ^= ((s1 << 4) | s2) << (i * 8)
        
        f_result = ((f_result << 11) | (f_result >> (32 - 11))) & 0xFFFFFFFF
        
        return (right, left ^ f_result)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста
        :param plaintext: исходный текст
        :return: зашифрованный текст
        """
        plaintext = plaintext.upper().replace('Ё', 'Е')
        ciphertext = ''
        
        for i in range(0, len(plaintext), 4):
            block = plaintext[i:i+4]
            if len(block) < 4:
                block += 'А' * (4 - len(block))
            
            left = sum(self.alphabet.index(ch) * (256 ** j) for j, ch in enumerate(block[:2]))
            right = sum(self.alphabet.index(ch) * (256 ** j) for j, ch in enumerate(block[2:4]))
            
            for round_num in range(8):
                round_key = self._create_round_key(round_num)
                left, right = self._feistel_round(left, right, round_key)
            
            left, right = right, left
            
            encrypted_block = ''
            for j in range(4):
                idx = (left >> (j * 8)) & 0xFF if j < 2 else (right >> ((j-2) * 8)) & 0xFF
                encrypted_block += self.alphabet[idx % self.alphabet_size]
            
            ciphertext += encrypted_block
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """Расшифровка текста"""
        return self.encrypt(ciphertext)


# ============================================================================
# ОБРАБОТЧИК ТЕКСТА И ИНТЕРФЕЙС
# ============================================================================

class TextProcessor:
    """Обработчик текста с заменой пунктуации"""
    
    PUNCTUATION_MAP = {
        '-': 'тире',
        '!': 'воскл',
        '?': 'вопр',
        '.': 'тчк',
        ',': 'зпт',
        ';': 'тчкзпт',
        ':': 'двтчк',
        '"': 'кавыч',
        "'": 'апостр',
        '(': 'скобл',
        ')': 'скобп',
        '[': 'квадл',
        ']': 'квадп',
    }
    
    @staticmethod
    def replace_punctuation(text: str) -> str:
        """
        Заменяет пунктуацию на текстовые обозначения
        :param text: исходный текст
        :return: текст с заменённой пунктуацией
        """
        result = text
        for punct, replacement in TextProcessor.PUNCTUATION_MAP.items():
            result = result.replace(punct, ' ' + replacement + ' ')
        return result


class CipherSelector:
    """Селектор доступных шифров"""
    
    @staticmethod
    def get_ciphers_dict():
        """Возвращает словарь доступных шифров"""
        return {
            'vigenere_key': {
                'name': 'Шифр Виженера (ключевое слово)',
                'class': VigenereCipher,
                'key_required': True,
                'description': 'Ключевое слово циклически повторяется для шифрования'
            },
            'vigenere_auto': {
                'name': 'Шифр Виженера (самоключ)',
                'class': VigenereAutokeyCipher,
                'key_required': True,
                'description': 'Открытый текст служит продолжением ключа (более стойкий)'
            },
            'tritemia': {
                'name': 'Шифр Тритемия',
                'class': TrithemiusCipher,
                'key_required': False,
                'description': 'Прогрессивный шифр с увеличивающимся сдвигом'
            },
            'belaso': {
                'name': 'Шифр Белазо',
                'class': BelasoCipher,
                'key_required': True,
                'description': 'Шифр с перестановленным алфавитом на каждой позиции'
            },
            'gost': {
                'name': 'S-блок ГОСТ Р 34.12-2015',
                'class': GOSTCipher,
                'key_required': True,
                'description': 'Современный блочный шифр с S-блоками'
            }
        }
    
    @staticmethod
    def display_menu():
        """Показывает меню выбора шифра"""
        ciphers = CipherSelector.get_ciphers_dict()
        print("\n" + "="*60)
        print("ПРОГРАММА ШИФРОВАНИЯ ТЕКСТА - МНОГОЗНАЧНАЯ ЗАМЕНА")
        print("="*60)
        print("\nДоступные методы шифрования:")
        for idx, (key, cipher_info) in enumerate(ciphers.items(), 1):
            print(f"{idx}. {cipher_info['name']}")
            print(f"   {cipher_info['description']}")
        print(f"{len(ciphers) + 1}. Выход")
    
    @staticmethod
    def select_cipher():
        """Позволяет пользователю выбрать шифр"""
        ciphers = CipherSelector.get_ciphers_dict()
        
        while True:
            CipherSelector.display_menu()
            try:
                choice = int(input("\nВыберите номер шифра: "))
                
                if choice == len(ciphers) + 1:
                    return None
                
                if 1 <= choice <= len(ciphers):
                    cipher_key = list(ciphers.keys())[choice - 1]
                    cipher_info = ciphers[cipher_key]
                    
                    if cipher_info['key_required']:
                        print(f"\nВводите ключ...")
                        key = input(f"Введите ключ для {cipher_info['name']}: ").strip()
                        if not key:
                            print("Ошибка: ключ не может быть пустым!")
                            continue
                        print(f"Ключ получен: {key}")
                        cipher_obj = cipher_info['class'](key)
                        print(f"Шифр инициализирован")
                        return cipher_obj
                    else:
                        try:
                            initial_shift = int(input("Введите начальный сдвиг (по умолчанию 0): ") or "0")
                            return cipher_info['class'](initial_shift)
                        except ValueError:
                            print("Ошибка: неверное значение сдвига!")
                            continue
                else:
                    print("Ошибка: выберите из предложенных вариантов!")
            except ValueError:
                print("Ошибка: введите число!")


def main():
    """Главная функция программы"""
    
    while True:
        cipher = CipherSelector.select_cipher()
        
        if cipher is None:
            print("\nДо свидания!")
            break
        
        print("\n" + "="*60)
        print("ВВОД ТЕКСТА")
        print("="*60)
        print("Введите текст для шифрования:")
        print("(Введите 'END' на новой строке для завершения ввода)")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        
        original_text = '\n'.join(lines)
        
        # Обработка пунктуации
        processed_text = TextProcessor.replace_punctuation(original_text)
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ")
        print("="*60)
        
        # Шифрование
        print(f"\nШифрование текста ({len(processed_text)} символов)...")
        encrypted_text = cipher.encrypt(processed_text)
        print("✓ Шифрование завершено")
        
        # Выводим результаты
        print(f"\nДлина оригинального текста: {len(original_text)} символов")
        print(f"Длина обработанного текста: {len(processed_text)} символов")
        print(f"\nОригинальный текст (первые 200 символов):")
        print(original_text[:200])
        
        print(f"\nОбработанный текст (первые 200 символов):")
        print(processed_text[:200])
        
        print(f"\nЗашифрованный текст (первые 200 символов):")
        print(encrypted_text[:200])
        
        # Расшифровка для проверки
        print("\n" + "-"*60)
        print("ПРОВЕРКА РАСШИФРОВКИ")
        print("-"*60)
        print(f"\nРасшифровка ({len(encrypted_text)} символов)...")
        
        try:
            decrypted_text = cipher.decrypt(encrypted_text)
            print("✓ Расшифровка завершена")
            if decrypted_text.upper() == processed_text.upper():
                print("✓ Расшифровка успешна! Текст совпадает с исходным.")
                print(f"\nРасшифрованный текст (первые 200 символов):")
                print(decrypted_text[:200])
            else:
                print("✗ Расшифровка отличается от исходного текста.")
                print("(Это возможно для некоторых шифров)")
        except Exception as e:
            print(f"Ошибка при расшифровке: {e}")
        
        # Сохранение результатов
        save = input("\nСохранить результаты в файл? (y/n): ")
        if save.lower() == 'y':
            try:
                filename = input("Введите имя файла (без расширения): ").strip()
                if filename:
                    with open(f"{filename}_results.txt", 'w', encoding='utf-8') as f:
                        f.write("="*60 + "\n")
                        f.write("РЕЗУЛЬТАТЫ ШИФРОВАНИЯ\n")
                        f.write("="*60 + "\n\n")
                        f.write(f"Тип шифра: {type(cipher).__name__}\n")
                        f.write(f"Длина текста: {len(original_text)} символов\n\n")
                        f.write("ОРИГИНАЛЬНЫЙ ТЕКСТ:\n")
                        f.write(original_text + "\n\n")
                        f.write("ОБРАБОТАННЫЙ ТЕКСТ:\n")
                        f.write(processed_text + "\n\n")
                        f.write("ЗАШИФРОВАННЫЙ ТЕКСТ:\n")
                        f.write(encrypted_text + "\n")
                    print(f"Результаты сохранены в файл {filename}_results.txt")
            except Exception as e:
                print(f"Ошибка при сохранении: {e}")
        
        # Продолжить?
        another = input("\nЗашифровать другой текст? (y/n): ")
        if another.lower() != 'y':
            print("\nДо свидания!")
            break


if __name__ == "__main__":
    main()
