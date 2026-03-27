#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Программа для шифрования и расшифровки текста
Поддерживает шифры: Атбаш, Цезарь, Полибия
Работает с русским алфавитом
"""

import os

class CipherProgram:
    def __init__(self):
        self.russian_alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюя'
        self.ru_upper = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        
        # Директория, где находится скрипт
        self.script_dir = os.path.dirname(os.3path.abspath(__file__))
        
        # Таблица замены пунктуации
        self.punctuation_map = {
            '-': 'тире',
            '!': 'воскл',
            '?': 'вопр',
            '.': 'тчк',
            ',': 'зпт'
        }
        
        # Обратная таблица для замены слов обратно в пунктуацию
        self.punctuation_reverse = {v: k for k, v in self.punctuation_map.items()}
        
        # Таблица Полибия для русского алфавита (6x6)
        self.polybius_table = [
            ['а', 'б', 'в', 'г', 'д', 'е'],
            ['ж', 'з', 'и', 'й', 'к', 'л'],
            ['м', 'н', 'о', 'п', 'р', 'с'],
            ['т', 'у', 'ф', 'х', 'ц', 'ч'],
            ['ш', 'щ', 'ъ', 'ы', 'ь', 'э'],
            ['ю', 'я', ' ', ' ', ' ', ' ']
        ]
        
        # Обратная таблица Полибия для быстрого поиска
        self.polybius_reverse = {}
        for i, row in enumerate(self.polybius_table):
            for j, char in enumerate(row):
                self.polybius_reverse[char] = (i + 1, j + 1)
    
    def _replace_punctuation_to_words(self, text):
        """Заменяет пунктуацию на словесные эквиваленты с пробелами"""
        result = text
        for punct, word in self.punctuation_map.items():
            result = result.replace(punct, f' {word} ')
        return result
    
    def _restore_words_to_punctuation(self, text):
        """Восстанавливает пунктуацию из словесных эквивалентов"""
        result = text
        for word, punct in self.punctuation_reverse.items():
            result = result.replace(f' {word} ', punct)
        return result
    
    def _replace_punctuation(self, text):
        """Заменяет пунктуацию на словесные эквиваленты"""
        result = text
        for punct, word in self.punctuation_map.items():
            result = result.replace(punct, f' {word} ')
        return result
    
    def _replace_punctuation_with_markers(self, text):
        """Заменяет пунктуацию на маркеры перед шифрованием"""
        result = text
        for punct, word in self.punctuation_map.items():
            result = result.replace(punct, f'§{word}§')
        return result
    
    def _restore_punctuation(self, text):
        """Восстанавливает пунктуацию из словесных эквивалентов"""
        result = text
        for word, punct in self.punctuation_reverse.items():
            result = result.replace(word, punct)
        return result
    
    def _restore_punctuation_from_markers(self, text):
        """Восстанавливает пунктуацию из маркеров после расшифровки"""
        result = text
        for punct, word in self.punctuation_map.items():
            result = result.replace(f'§{word}§', punct)
        return result
    
    def _restore_punctuation_markers(self, text):
        """Восстанавливает пунктуацию из маркеров"""
        result = text
        for punct, word in self.punctuation_map.items():
            result = result.replace(f"§{word}§", word)
        return result
    
    def _read_from_file(self, filename):
        """Читает текст из файла"""
        filepath = os.path.join(self.script_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"\nОшибка: Файл '{filename}' не найден в директории {self.script_dir}")
            return None
        except Exception as e:
            print(f"\nОшибка при чтении файла: {e}")
            return None
    
    def _write_to_file(self, filename, content):
        """Записывает текст в файл"""
        filepath = os.path.join(self.script_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✓ Файл '{filename}' успешно создан/обновлен в {self.script_dir}")
            return True
        except Exception as e:
            print(f"\nОшибка при записи в файл: {e}")
            return False
    
    def _process_file_with_cipher(self, read_func, encrypt_func, *args):
        """Обработка файла с помощью шифра"""
        text = self._read_from_file('test1.txt')
        if text is None:
            return
        
        # Берем первые 1000 символов
        text_to_encrypt = text[:1000]
        char_count = len(text_to_encrypt)
        
        print(f"\nОбработано символов: {char_count}")
        
        # Шифруем текст
        encrypted = encrypt_func(text_to_encrypt, *args)
        
        # Сохраняем результат
        self._write_to_file('allchip.txt', encrypted)
    
    def atbash_encrypt(self, text):
        """Шифр Атбаш - замена буквы на противоположную в алфавите"""
        # Сначала заменяем пунктуацию на словесные эквиваленты
        text = self._replace_punctuation_to_words(text)
        
        result = []
        text_lower = text.lower()
        
        for char in text_lower:
            if char in self.russian_alphabet:
                index = self.russian_alphabet.index(char)
                # Меняем на букву с конца алфавита
                result.append(self.russian_alphabet[-(index + 1)])
            else:
                # Оставляем пробелы и остальное без изменений
                result.append(char)
        
        return ''.join(result)
    
    def atbash_decrypt(self, text):
        """Расшифровка Атбаша (алгоритм симметричный)"""
        decrypted = self.atbash_encrypt(text)
        return self._restore_words_to_punctuation(decrypted)
    
    def caesar_encrypt(self, text, shift):
        """Шифр Цезаря - сдвиг букв на заданное количество позиций"""
        # Сначала заменяем пунктуацию на словесные эквиваленты
        text = self._replace_punctuation_to_words(text)
        
        result = []
        text_lower = text.lower()
        shift = shift % len(self.russian_alphabet)
        
        for char in text_lower:
            if char in self.russian_alphabet:
                index = self.russian_alphabet.index(char)
                new_index = (index + shift) % len(self.russian_alphabet)
                result.append(self.russian_alphabet[new_index])
            else:
                # Оставляем пробелы и остальное без изменений
                result.append(char)
        
        return ''.join(result)
    
    def caesar_decrypt(self, text, shift):
        """Расшифровка Цезаря - обратный сдвиг"""
        decrypted = self.caesar_encrypt(text, -shift)
        return self._restore_words_to_punctuation(decrypted)
    
    def polybius_encrypt(self, text):
        """Шифр Полибия - преобразование букв в координаты таблицы"""
        # Сначала заменяем пунктуацию на словесные эквиваленты
        text = self._replace_punctuation_to_words(text)
        
        result = []
        text_lower = text.lower()
        
        for char in text_lower:
            if char in self.polybius_reverse:
                row, col = self.polybius_reverse[char]
                result.append(f"{row}{col}")
            elif char == ' ':
                result.append('56')  # Пробел - координата (5, 6)
            else:
                result.append(f"XX")  # Неизвестный символ
        
        return ' '.join(result)
    
    def polybius_decrypt(self, text):
        """Расшифровка Полибия"""
        coordinates = text.split()
        result = []
        
        for coord in coordinates:
            if len(coord) == 2 and coord.isdigit():
                row = int(coord[0]) - 1
                col = int(coord[1]) - 1
                
                if 0 <= row < len(self.polybius_table) and 0 <= col < len(self.polybius_table[0]):
                    result.append(self.polybius_table[row][col])
                else:
                    result.append('?')
            else:
                result.append('?')
        
        decrypted = ''.join(result)
        return self._restore_words_to_punctuation(decrypted)
    
    def show_menu(self):
        """Выводит главное меню"""
        print("\n" + "="*60)
        print("      ПРОГРАММА ШИФРОВАНИЯ И РАСШИФРОВКИ")
        print("="*60)
        print("\n1. Шифр Атбаш")
        print("2. Шифр Цезаря")
        print("3. Шифр Полибия")
        print("4. О шифрах")
        print("5. Выход")
        print("\n" + "-"*60)
    
    def show_cipher_menu(self, cipher_name):
        """Меню для конкретного шифра"""
        print(f"\n{cipher_name}:")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Вернуться в главное меню")
    
    def show_info(self):
        """Информация о шифрах"""
        print("\n" + "="*60)
        print("ИНФОРМАЦИЯ О ШИФРАХ")
        print("="*60)
        print("\n1. АТБАШ:")
        print("   - Каждая буква заменяется на букву с противоположной позиции")
        print("   - А↔Я, Б↔Ю и так далее")
        print("   - Более древний еврейский шифр")
        print("\n2. ЦЕЗАРЬ:")
        print("   - Каждая буква сдвигается на фиксированное количество позиций")
        print("   - Используется ключ (числовое смещение)")
        print("   - Простой, но уязвимый к атакам перебора")
        print("\n3. ПОЛИБИЯ:")
        print("   - Каждая буква заменяется парой цифр (строка, столбец)")
        print("   - Букво преобразуются в таблицу 5×6")
        print("   - Часто используется как промежуточный шаг в криптографии")
        print("\n" + "-"*60)
    
    def process_atbash(self):
        """Обработка операций с Атбашем"""
        while True:
            self.show_cipher_menu("Шифр Атбаш")
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "1":
                text = input("\nВведите текст для шифрования: ").strip()
                if text:
                    encrypted = self.atbash_encrypt(text)
                    print(f"\nЗашифрованный текст: {encrypted}")
            elif choice == "2":
                text = input("\nВведите текст для расшифровки: ").strip()
                if text:
                    decrypted = self.atbash_decrypt(text)
                    print(f"\nРасшифрованный текст: {decrypted}")
            elif choice == "3":
                break
            else:
                print("\nНеверный выбор. Попробуйте снова.")
    
    def process_caesar(self):
        """Обработка операций с Цезарем"""
        while True:
            self.show_cipher_menu("Шифр Цезаря")
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "1":
                text = input("\nВведите текст для шифрования: ").strip()
                try:
                    shift = int(input("Введите значение ключа (сдвиг 1-32): ").strip())
                    if 1 <= shift <= 32:
                        encrypted = self.caesar_encrypt(text, shift)
                        print(f"\nЗашифрованный текст: {encrypted}")
                        print(f"Ключ: {shift}")
                    else:
                        print("\nОшибка: Ключ должен быть от 1 до 32")
                except ValueError:
                    print("\nОшибка: введите число")
            elif choice == "2":
                text = input("\nВведите текст для расшифровки: ").strip()
                try:
                    shift = int(input("Введите значение ключа (сдвиг 1-32): ").strip())
                    if 1 <= shift <= 32:
                        decrypted = self.caesar_decrypt(text, shift)
                        print(f"\nРасшифрованный текст: {decrypted}")
                    else:
                        print("\nОшибка: Ключ должен быть от 1 до 32")
                except ValueError:
                    print("\nОшибка: введите число")
            elif choice == "3":
                break
            else:
                print("\nНеверный выбор. Попробуйте снова.")
    
    def process_polybius(self):
        """Обработка операций с Полибием"""
        while True:
            self.show_cipher_menu("Шифр Полибия")
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "1":
                text = input("\nВведите текст для шифрования: ").strip()
                if text:
                    encrypted = self.polybius_encrypt(text)
                    print(f"\nЗашифрованный текст: {encrypted}")
            elif choice == "2":
                text = input("\nВведите закодированный текст (цифры через пробел): ").strip()
                if text:
                    decrypted = self.polybius_decrypt(text)
                    print(f"\nРасшифрованный текст: {decrypted}")
            elif choice == "3":
                break
            else:
                print("\nНеверный выбор. Попробуйте снова.")
    
    def run(self):
        """Главный цикл программы"""
        while True:
            self.show_menu()
            choice = input("Выберите шифр (1-5): ").strip()
            
            if choice == "1":
                self.process_atbash()
            elif choice == "2":
                self.process_caesar()
            elif choice == "3":
                self.process_polybius()
            elif choice == "4":
                self.show_info()
            elif choice == "5":
                print("\nДо свидания!\n")
                break
            else:
                print("\nНеверный выбор. Попробуйте снова.")


def main():
    """Точка входа программы"""
    program = CipherProgram()
    program.run()


if __name__ == "__main__":
    main()
