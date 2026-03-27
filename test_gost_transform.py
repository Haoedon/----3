"""
Тестирование t-преобразования ГОСТ Р 34.12-2015 с заданными примерами
"""

# S-блоки ГОСТ Р 34.12-2015
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


def apply_sbox(nibble, sbox_num):
    """Применение S-блока к полубайту"""
    sbox_idx = sbox_num % len(SBOX)
    return SBOX[sbox_idx][nibble & 0x0F]


def t_transform(value):
    """t-преобразование для 32-битного значения"""
    result = 0
    
    # Обрабатываем 4 байта
    for byte_idx in range(4):
        # Извлекаем байт
        byte_val = (value >> (byte_idx * 8)) & 0xFF
        
        # Разбиваем на полубайты
        low_nibble = byte_val & 0x0F
        high_nibble = (byte_val >> 4) & 0x0F
        
        # Применяем S-блоки
        sbox_num_low = (byte_idx * 2) % 8
        sbox_num_high = (byte_idx * 2 + 1) % 8
        
        transformed_low = apply_sbox(low_nibble, sbox_num_low)
        transformed_high = apply_sbox(high_nibble, sbox_num_high)
        
        # Собираем байт
        transformed_byte = (transformed_high << 4) | transformed_low
        
        # Добавляем в результат
        result |= transformed_byte << (byte_idx * 8)
    
    return result


def format_hex(value):
    """Форматирование значения в hex"""
    return f"0x{value:08x}"


# Примеры из задания
test_cases = [
    (0xfdb97531, 0x2a196f34),
    (0x2a196f34, 0xebd9f03a),
    (0xebd9f03a, 0xb039bb3d),
    (0xb039bb3d, 0x68695433),
]

print("Проверка примеров t-преобразования ГОСТ:")
print("=" * 60)

all_pass = True
for input_val, expected_val in test_cases:
    result = t_transform(input_val)
    passed = result == expected_val
    all_pass = all_pass and passed
    
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status}")
    print(f"  Вход:      {format_hex(input_val)}")
    print(f"  Ожидаемо:  {format_hex(expected_val)}")
    print(f"  Получено:  {format_hex(result)}")
    
    if not passed:
        print(f"  Разница:   {format_hex(result ^ expected_val)}")

print("\n" + "=" * 60)
if all_pass:
    print("Все примеры прошли проверку! ✓")
else:
    print("Некоторые примеры не прошли проверку ✗")
    print("\nПопытаемся найти правильную схему преобразования...")
    
    # Дополнительная налладка
    print("\nДополнительный анализ:")
    for input_val, expected_val in test_cases:
        print(f"\nВход: {format_hex(input_val)} ({bin(input_val)})")
        print(f"Ожидаемо: {format_hex(expected_val)} ({bin(expected_val)})")
        
        # Анализируем каждый байт
        for i in range(4):
            in_byte = (input_val >> (i * 8)) & 0xFF
            exp_byte = (expected_val >> (i * 8)) & 0xFF
            print(f"  Байт {i}: {in_byte:02x} -> {exp_byte:02x}")
