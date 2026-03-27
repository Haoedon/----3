"""
Тест для проверки работы классов
"""

from main import VigenereCipher, TextProcessor

# Простой тест
print("Проверка класса VigenereCipher...")

try:
    cipher = VigenereCipher("КЛЮЧ")
    print(f"✓ Класс инициализирован")
    
    plaintext = "ПРИВЕТ МИР"
    print(f"\nОригинальный текст: {plaintext}")
    
    encrypted = cipher.encrypt(plaintext)
    print(f"Зашифрованный текст: {encrypted}")
    
    decrypted = cipher.decrypt(encrypted)
    print(f"Расшифрованный текст: {decrypted}")
    
    if decrypted == plaintext.upper():
        print("✓ Шифрование работает корректно!")
    else:
        print("✗ Ошибка: тексты не совпадают")
    
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# Тест обработки пунктуации
print("\n" + "="*50)
print("Проверка обработки пунктуации...")

text_with_punct = "Привет, мир! Как дела?"
print(f"Исходный текст: {text_with_punct}")

processed = TextProcessor.replace_punctuation(text_with_punct)
print(f"Обработанный текст: {processed}")

print("\n✓ Все проверки завершены")
