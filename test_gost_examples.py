"""
Демонстрация t-преобразования ГОСТ Р 34.12-2015
с примерами из задания
"""

import sys
sys.path.insert(0, r'c:\кмзи3')

from main_fixed import GOSTCipher

# Создаем экземпляр ГОСТ шифра
gost = GOSTCipher()

# Примеры t-преобразования из задания
test_cases = [
    (0xfdb97531, 0x2a196f34),
    (0x2a196f34, 0xebd9f03a),
    (0xebd9f03a, 0xb039bb3d),
    (0xb039bb3d, 0x68695433),
]

print("=" * 70)
print("t-преобразование ГОСТ Р 34.12-2015")
print("=" * 70)
print("\nПримеры из задания:\n")

all_pass = True
for input_val, expected in test_cases:
    result = gost.t_transform(input_val)
    match = "✓ PASS" if result == expected else "✗ FAIL"
    all_pass = all_pass and (result == expected)
    
    print(f"{match}  t(0x{input_val:08x}) = 0x{result:08x}")
    if result != expected:
        print(f"        Ожидалось: 0x{expected:08x}")
        print(f"        Разница:   0x{result ^ expected:08x}")

print("\n" + "=" * 70)
if all_pass:
    print("✓ Все примеры прошли проверку!")
else:
    print("✗ Некоторые примеры не совпадают")
    print("\nПримечание: Это означает, что используемые S-блоки или порядок")
    print("их применения отличается от стандарта ГОСТ Р 34.12-2015.")
    print("Пожалуйста, проверьте правильность S-блоков и алгоритма.")

print("\n" + "=" * 70)
print("Демонстрация шифрования текста:")
print("=" * 70)

# Пример шифрования текста
text = "ПРИВЕТ"
print(f"\nОригинальный текст: {text}")
encrypted = gost.encrypt(text)
print(f"Зашифрованный текст: {encrypted}")
