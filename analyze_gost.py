"""
Анализ и восстановление S-блоков из примеров t-преобразования
"""

def analyze_and_recover_sbox():
    """Восстанавливает S-блоки из предоставленных примеров"""
    
    test_cases = [
        (0xfdb97531, 0x2a196f34),
        (0x2a196f34, 0xebd9f03a),
        (0xebd9f03a, 0xb039bb3d),
        (0xb039bb3d, 0x68695433),
    ]
    
    print("=" * 70)
    print("АНАЛИЗ ПРИМЕРОВ t-ПРЕОБРАЗОВАНИЯ")
    print("=" * 70)
    
    # Словарь для восстановления отображений: (позиция, входное значение) -> выходное
    mappings = {}
    
    for input_val, output_val in test_cases:
        print(f"\nt({input_val:08x}) = {output_val:08x}")
        print("-" * 50)
        
        for pos in range(8):
            # Извлекаем полубайты (little-endian: от младшего к старшему)
            in_nibble = (input_val >> (pos * 4)) & 0x0F
            out_nibble = (output_val >> (pos * 4)) & 0x0F
            
            key = (pos, in_nibble)
            
            # Проверяем на конфликты
            if key in mappings:
                if mappings[key] != out_nibble:
                    print(f"  КОНФЛИКТ на позиции {pos}: {in_nibble:x} -> "
                          f"{mappings[key]:x} vs {out_nibble:x}")
            else:
                mappings[key] = out_nibble
            
            print(f"  Позиция {pos}: {in_nibble:x} -> {out_nibble:x}")
    
    print("\n" + "=" * 70)
    print("ВОССТАНОВЛЕННЫЕ S-БЛОКИ")
    print("=" * 70)
    
    # Строим S-блоки из отображений
    sbox_recovered = [list(range(16)) for _ in range(8)]  # Инициализируем
    
    for (pos, in_val), out_val in mappings.items():
        sbox_recovered[pos][in_val] = out_val
    
    print("\nВосстановленные S-блоки (полностью из примеров):")
    for i, sbox in enumerate(sbox_recovered):
        # Показываем только установленные значения
        set_mappings = []
        all_set = True
        for in_val, out_val in enumerate(sbox):
            if (i, in_val) in mappings:
                set_mappings.append(f"[{in_val}]={out_val}")
            else:
                all_set = False
        
        if set_mappings or not all_set:
            print(f"\nSBOX[{i}] (из примеров):")
            print(f"  " + ", ".join(set_mappings) if set_mappings else "  (нет данных)")
    
    print("\n" + "=" * 70)
    print("СТАТИСТИКА")
    print("=" * 70)
    print(f"Всего уникальных отображений (позиция, вход)->выход: {len(mappings)}")
    print(f"Примеров преобразований: {len(test_cases)}")
    print(f"Всего полубайтов в примерах: {len(test_cases) * 8}")
    
    return mappings, sbox_recovered


if __name__ == "__main__":
    mappings, sbox = analyze_and_recover_sbox()
    
    print("\n" + "=" * 70)
    print("ИСПОЛЬЗУЕТСЯ В ПРОГРАММЕ:")
    print("=" * 70)
    print("""
Текущая реализация HOSTCipher.t_transform в main_fixed.py
применяет S-блоки из стандарта GOST R 34.12-2015.

Для корректной реализации с примерами из задания,
могут потребоваться скорректированные S-блоки.

Все 8 S-блоков должны быть определены для всех 16 входных значений (0-15).
    """)
