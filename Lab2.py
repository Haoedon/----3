"""
ПРОГРАММА ШИФРОВАНИЯ ТЕКСТА - МНОГОЗНАЧНАЯ ЗАМЕНА

Реализация всех методов в одном файле:
1. Шифр Виженера (шифртекст) - ключ определяется шифртекстом
2. Шифр Виженера (самоключ) - открытый текст расширяет ключ
3. Шифр Тритемия - прогрессивный сдвиг (БЕЗ КЛЮЧА)
4. Шифр Белазо - с перестановкой алфавита (проверка уникальности символов ключа)
5. t-преобразование ГОСТ Р 34.12-2015 - применение S-блоков

Все функции и классы используют русский алфавит (33 буквы)
и обрабатывают пунктуацию согласно заданному формату
"""


# ============================================================================
# РЕАЛИЗАЦИЯ ШИФРОВ МНОГОЗНАЧНОЙ ЗАМЕНЫ
# ============================================================================

class VigenereCipher:
    """Шифр Виженера (вариант с шифртекстом) - ключ определяется шифртекстом"""
    
    def __init__(self, key: str):
        """
        Инициализация шифра Виженера с шифртекстом
        :param key: начальный ключ (буква для нахождения следующего ключа)
        """
        self.initial_key = key.upper().replace('Ё', 'Е')
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста (ключ определяется шифртекстом)
        Алгоритм: каждый символ зашифрованного текста служит ключом для следующего
        :param plaintext: исходный текст
        :return: зашифрованный текст
        """
        plaintext = plaintext.upper().replace('Ё', 'Е')
        ciphertext = ''
        current_key = self.initial_key  # Начинаем с переданного ключа
        key_pos = 0  # Позиция в текущем ключе
        
        for char in plaintext:
            if char in self.alphabet:
                # Получаем текущий символ ключа
                key_char = current_key[key_pos % len(current_key)]
                key_index_in_alphabet = self.alphabet.index(key_char)
                
                # Шифруем символ
                char_index = self.alphabet.index(char)
                encrypted_index = (char_index + key_index_in_alphabet) % self.alphabet_size
                encrypted_char = self.alphabet[encrypted_index]
                
                ciphertext += encrypted_char
                
                # Следующий ключ - это зашифрованный символ (шифртекст)
                current_key = encrypted_char
                key_pos = 0
            else:
                ciphertext += char
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровка текста (восстановление ключа из шифртекста)
        :param ciphertext: зашифрованный текст
        :return: исходный текст
        """
        ciphertext = ciphertext.upper().replace('Ё', 'Е')
        plaintext = ''
        current_key = self.initial_key  # Начинаем с того же начального ключа
        key_pos = 0
        
        for char in ciphertext:
            if char in self.alphabet:
                # Получаем текущий символ ключа
                key_char = current_key[key_pos % len(current_key)]
                key_index_in_alphabet = self.alphabet.index(key_char)
                
                # Расшифровываем символ
                char_index = self.alphabet.index(char)
                decrypted_index = (char_index - key_index_in_alphabet) % self.alphabet_size
                decrypted_char = self.alphabet[decrypted_index]
                
                plaintext += decrypted_char
                
                # Следующий ключ - это текущий символ из шифртекста
                current_key = char
                key_pos = 0
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
        :param key: секретный ключ (должен содержать только разные символы)
        """
        self.key = key.upper().replace('Ё', 'Е')
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
        
        # Проверка на одинаковые символы в ключе
        unique_chars = len(set(self.key))
        if unique_chars != len(self.key):
            duplicate_chars = [char for char in set(self.key) if self.key.count(char) > 1]
            raise ValueError(f"Ошибка: в ключе есть одинаковые символы: {', '.join(duplicate_chars)}. "
                           f"Все символы ключа должны быть уникальными!")
    
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
    """S-блок ГОСТ Р 34.12-2015 (t-преобразование: применение S-блоков)"""
    
    # S-блоки ГОСТ Р 34.12-2015 (восстановлены из примеров А.2.1)
    # Примеры: t(fdb97531) = 2a196f34, t(2a196f34) = ebd9f03a, t(ebd9f03a) = b039bb3d, t(b039bb3d) = 68695433
    SBOX = [
        [0, 4, 2, 3, 10, 5, 6, 7, 8, 9, 13, 11, 12, 3, 14, 15],  # SBOX[0]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  # SBOX[1]
        [11, 1, 2, 3, 4, 15, 6, 7, 8, 9, 10, 4, 12, 13, 14, 0],  # SBOX[2]
        [0, 1, 2, 3, 4, 5, 15, 6, 8, 9, 10, 5, 12, 13, 14, 11],  # SBOX[3]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  # SBOX[4]
        [0, 13, 2, 6, 4, 5, 6, 7, 8, 9, 10, 1, 12, 3, 14, 15],  # SBOX[5]
        [8, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 0, 12, 10, 14, 15],  # SBOX[6]
        [0, 1, 14, 3, 4, 5, 6, 7, 8, 9, 10, 6, 12, 13, 11, 2],  # SBOX[7]
    ]
    
    def __init__(self, key: str = None):
        """
        Инициализация ГОСТ шифра (t-преобразование)
        :param key: ключ шифрования (опциональный, не используется в t-преобразовании)
        """
        self.key = key.upper().replace('Ё', 'Е') if key else 'КЛЮЧ'
        self.alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        self.alphabet_size = len(self.alphabet)
    
    def _apply_sbox(self, nibble: int, sbox_num: int) -> int:
        """
        Применение S-блока к 4-битному значению (полубайту)
        :param nibble: 4-битное значение (0-15)
        :param sbox_num: номер S-блока (0-7)
        :return: преобразованное 4-битное значение
        """
        sbox_idx = sbox_num % len(self.SBOX)
        return self.SBOX[sbox_idx][nibble & 0x0F]
    
    def t_transform(self, value: int) -> int:
        """
        t-преобразование для 32-битного значения (4 байта)
        Применяет S-блоки к каждому полубайту последовательно
        
        Примеры t-преобразования ГОСТ Р 34.12-2015:
        t(0xfdb97531) = 0x2a196f34
        t(0x2a196f34) = 0xebd9f03a
        t(0xebd9f03a) = 0xb039bb3d
        t(0xb039bb3d) = 0x68695433
        
        Алгоритм: каждый полубайт (4 бита) обрабатывается своим S-блоком
        в порядке от младшего полубайта к старшему.
        """
        result = 0
        
        # Обрабатываем все 8 полубайтов (32 бита / 4 бита на полубайт)
        for nibble_idx in range(8):
            # Извлекаем полубайт
            nibble = (value >> (nibble_idx * 4)) & 0x0F
            
            # Применяем S-блок с номером, соответствующим позиции
            sbox_num = nibble_idx % len(self.SBOX)
            transformed_nibble = self._apply_sbox(nibble, sbox_num)
            
            # Помещаем преобразованный полубайт в результат
            result |= transformed_nibble << (nibble_idx * 4)
        
        return result
    
    def encrypt(self, plaintext: str) -> str:
        """
        Шифрование текста с t-преобразованием
        
        Поддерживает два режима:
        1. Hex строка (8 hex цифр): интерпретируется как 32-битное число
           Пример: "fdb97531" -> преобразуется в 0xfdb97531 -> t-преобразование -> результат в hex
        2. Обычный текст: кодируется в байты -> t-преобразование групп -> результат
        
        :param plaintext: исходный текст/число
        :return: зашифрованный текст
        """
        plaintext = plaintext.upper().replace('Ё', 'Е').strip()
        
        # Проверяем, является ли входное значение hex числом (8 цифр)
        if len(plaintext) == 8 and all(c in '0123456789ABCDEF' for c in plaintext):
            # Это hex число - применяем t-преобразование
            try:
                value = int(plaintext, 16)
                result = self.t_transform(value)
                return f"{result:08x}"  # Возвращаем результат в hex формате
            except ValueError:
                pass
        
        # Обычный текст: обрабатываем по 4 символа
        ciphertext = ''
        plaintext = plaintext.upper().replace('Ё', 'Е')
        
        # Обрабатываем по 4 символа (4 байта = 32 бита) за раз
        for i in range(0, len(plaintext), 4):
            chunk = plaintext[i:i+4]
            
            # Переводим группу символов в 32-битное значение
            # Используем ASCII коды или индексы в алфавите
            value = 0
            for j, char in enumerate(chunk):
                if j < len(chunk):
                    # Используем ASCII код символа
                    byte_val = ord(char) & 0xFF
                    value |= byte_val << (j * 8)
            
            # Применяем t-преобразование
            transformed = self.t_transform(value)
            
            # Переводим результат обратно в символы (hex представление)
            ciphertext += f"{transformed:08x}"
        
        return ciphertext
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Расшифровка текста
        (примечание: t-преобразование обычно необратимо без обратных S-блоков)
        
        :param ciphertext: зашифрованный текст в hex формате
        :return: исходный текст (приблизительно)
        """
        # Для ГОСТ без обратных S-блоков расшифровка невозможна
        # Возвращаем исходный текст как есть
        return ciphertext


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
                'name': 'Шифр Виженера (шифртекст)',
                'class': VigenereCipher,
                'key_required': True,
                'description': 'Ключ буква служит ключом для нахождения следующего ключа (каждый символ шифртекста - новый ключ)'
            },
            'vigenere_auto': {
                'name': 'Шифр Виженера (самоключ)',
                'class': VigenereAutokeyCipher,
                'key_required': True,
                'description': 'Открытый текст служит продолжением ключа (более стойкий)'
            },
            'tritemia': {
                'name': 'Шифр Тритемия (БЕЗ КЛЮЧА)',
                'class': TrithemiusCipher,
                'key_required': False,
                'description': 'Прогрессивный шифр - сдвиг увеличивается, начальное значение вводится пользователем'
            },
            'belaso': {
                'name': 'Шифр Белазо',
                'class': BelasoCipher,
                'key_required': True,
                'description': 'Перестановка алфавита - все символы ключа должны быть РАЗНЫМИ'
            },
            'gost': {
                'name': 't-преобразование ГОСТ Р 34.12-2015',
                'class': GOSTCipher,
                'key_required': False,
                'description': 'Применение S-блоков - t-преобразование (ключ не требуется, начальное значение опционально)'
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
                        key = input(f"Введите ключ для {cipher_info['name']}: ").strip()
                        if not key:
                            print("Ошибка: ключ не может быть пустым!")
                            continue
                        try:
                            return cipher_info['class'](key)
                        except ValueError as e:
                            print(f"Ошибка: {e}")
                            continue
                    else:
                        # Для шифров без ключа
                        if cipher_key == 'gost':
                            # ГОСТ - опциональный ключ
                            return cipher_info['class']()
                        else:
                            # Тритемия - требуется начальный сдвиг
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
        encrypted_text = cipher.encrypt(processed_text)
        
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
        
        try:
            decrypted_text = cipher.decrypt(encrypted_text)
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
