"""
Простой тест двух вариантов Виженера
"""

# Копируем необходимые классы из main.py
import sys
sys.path.insert(0, 'c:\\кмзи3')

from main import VigenereCipher, VigenereAutokeyСipher, TextProcessor

print("="*70)
print("СРАВНЕНИЕ ДВУХ ВАРИАНТОВ ШИФРА ВИЖЕНЕРА")
print("="*70)

# Тестовый текст
plaintext = "КОЛЬЦО ВСЕМОГУЩЕСТВЕННОГО ВЛАДЫКИ СВЕТЛОГО"
key = "КОЛЬЦО"

print(f"\nОригинальный текст: {plaintext}")
print(f"Ключ: {key}\n")

# 1. Вариант с ключевым словом
print("-" * 70)
print("1. ШИФР ВИЖЕНЕРА - ВАРИАНТ С КЛЮЧЕВЫМ СЛОВОМ")
print("-" * 70)
print("Описание: Ключ циклически повторяется")
print()

cipher_key = VigenereCipher(key)
encrypted_key = cipher_key.encrypt(plaintext)
decrypted_key = cipher_key.decrypt(encrypted_key)

print(f"Зашифрованный: {encrypted_key}")
print(f"Расшифрованный: {decrypted_key}")
print(f"Проверка: {'✓ УСПЕШНО' if decrypted_key == plaintext.upper() else '✗ ОШИБКА'}")

# 2. Вариант с самоключом
print("\n" + "-" * 70)
print("2. ШИФР ВИЖЕНЕРА - ВАРИАНТ С САМОКЛЮЧОМ")
print("-" * 70)
print("Описание: Открытый текст служит продолжением ключа")
print()

cipher_auto = VigenereAutokeyСipher(key)
encrypted_auto = cipher_auto.encrypt(plaintext)
decrypted_auto = cipher_auto.decrypt(encrypted_auto)

print(f"Зашифрованный: {encrypted_auto}")
print(f"Расшифрованный: {decrypted_auto}")
print(f"Проверка: {'✓ УСПЕШНО' if decrypted_auto == plaintext.upper() else '✗ ОШИБКА'}")

# 3. Сравнение результатов
print("\n" + "-" * 70)
print("3. СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
print("-" * 70)
print(f"Оригинальный: {plaintext}")
print(f"С ключевым словом: {encrypted_key}")
print(f"С самоключом:      {encrypted_auto}")
print(f"\nТексты отличаются: {'✓ ДА' if encrypted_key != encrypted_auto else '✗ НЕТ'}")

# 4. Тест на большом тексте (1000+ символов)
print("\n" + "="*70)
print("ТЕСТ НА БОЛЬШОМ ТЕКСТЕ (1000+ СИМВОЛОВ)")
print("="*70)

large_text = """
КРИПТОГРАФИЯ ЯВЛЯЕТСЯ ДРЕВНЕЙ НАУКОЙ О ЗАЩИТЕ ИНФОРМАЦИИ. 
ЕЩЕ В ДРЕВНИХ ВРЕМЕНАХ ЛЮДИ ЧУВСТВОВАЛИ НЕОБХОДИМОСТЬ СКРЫВАТЬ ВАЖНУЮ ИНФОРМАЦИЮ. 
ДРЕВНИЕ ЕГИПТЯНЕ И ГРЕКИ ИСПОЛЬЗОВАЛИ РАЗЛИЧНЫЕ МЕТОДЫ ШИФРОВАНИЯ. 
ОДИН ИЗ САМЫХ ИЗВЕСТНЫХ ПРИМЕРОВ - ШИФР ЦЕЗАРЯ, ИСПОЛЬЗУЕМЫЙ РИМСКИМ ПОЛКОВОДЦЕМ. 
ЭТОТ МЕТОД ЗАКЛЮЧАЛСЯ В ПРОСТОЙ ЗАМЕНЕ КАЖДОЙ БУКВЫ НА БУКВУ, РАСПОЛОЖЕННУЮ 
НА ФИКСИРОВАННОЕ ЧИСЛО ПОЗИЦИЙ ДАЛЬШЕ В АЛФАВИТЕ. НАПРИМЕР, ПРИ СДВИГЕ НА ТРИ 
ПОЗИЦИИ БУКВА А СТАНОВИЛАСЬ В, БУКВА В СТАНОВИЛАСЬ Г, И ТАК ДАЛЕЕ ПО КРУГУ. 
НЕСМОТРЯ НА СВОЮ ПРОСТОТУ, ЭТОТ ШИФР ОБЕСПЕЧИВАЛ ДОСТАТОЧНУЮ ЗАЩИТУ. 
В СРЕДНИЕ ВЕКА КРИПТОГРАФИЯ ПОЛУЧИЛА РАЗВИТИЕ С ПОЯВЛЕНИЕМ ПОЛИАЛФАВИТНЫХ ШИФРОВ, 
КОТОРЫЕ ПРЕДСТАВЛЯЛИ СОБОЙ ЕСТЕСТВЕННУЮ ЭВОЛЮЦИЮ. САМЫЙ ЗНАМЕНИТЫЙ ИЗ НИХ - 
ЭТО ШИФР ВИЖЕНЕРА, СОЗДАННЫЙ ФРАНЦУЗСКИМ ДИПЛОМАТОМ И КРИПТОГРАФОМ БЛЕЗОМ ДЕ ВИЖЕНЕРОМ 
В ШЕСТНАДЦАТОМ ВЕКЕ. ЭТОТ РЕВОЛЮЦИОННЫЙ ШИФР ИСПОЛЬЗОВАЛ КЛЮЧЕВОЕ СЛОВО ДЛЯ ИЗМЕНЕНИЯ 
ВЕЛИЧИНЫ СДВИГА НА КАЖДОЙ ПОЗИЦИИ ТЕКСТА, ЧТО ЗНАЧИТЕЛЬНО ПОВЫШАЛО ЕГО СТОЙКОСТЬ.
""".upper().replace('\n', ' ').replace('  ', ' ')

print(f"Длина текста: {len(large_text)} символов")
print(f"Применяем оба варианта Виженера...\n")

key_large = "КРИПТОГРАФИЯ"

cipher_key_large = VigenereCipher(key_large)
encrypted_large_key = cipher_key_large.encrypt(large_text)
decrypted_large_key = cipher_key_large.decrypt(encrypted_large_key)

cipher_auto_large = VigenereAutokeyСipher(key_large)
encrypted_large_auto = cipher_auto_large.encrypt(large_text)
decrypted_large_auto = cipher_auto_large.decrypt(encrypted_large_auto)

print(f"Вариант с ключевым словом:")
print(f"  Шифрование: ✓")
print(f"  Расшифровка: {'✓' if decrypted_large_key == large_text else '✗'}")
print(f"  Первые 100 символов: {encrypted_large_key[:100]}...")

print(f"\nВариант с самоключом:")
print(f"  Шифрование: ✓")
print(f"  Расшифровка: {'✓' if decrypted_large_auto == large_text else '✗'}")
print(f"  Первые 100 символов: {encrypted_large_auto[:100]}...")

print("\n" + "="*70)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*70)
