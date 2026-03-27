import sys
from itertools import zip_longest

# =====================================================================
#   КОНСТАНТЫ
# =====================================================================
ALPHABET = ["а", "б", "в", "г", "д", "е", "ж", "з", "и", "й", "к", "л", "м",
            "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ",
            "ъ", "ы", "ь", "э", "ю", "я"]

PUNCT_MAP = {
    '.': 'тчк', ',': 'зпт', ';': 'тчз', '?': 'впр', '!': 'вск',
    '"': 'квч', '-': 'тире', '(': 'скоб', ')': 'скобз', "'": 'апстр', ' ': 'прбл'
}
REV_PUNCT_MAP = {v: k for k, v in PUNCT_MAP.items()}


# =====================================================================
#   ПРЕОБРАЗОВАНИЕ ТЕКСТА
# =====================================================================
def text_to_bits(text: str) -> str:
    """Конвертирует русские буквы в 5-битные коды."""
    print(f"\n--- ПРЕОБРАЗОВАНИЕ ТЕКСТА В БИТЫ ---")
    result = ""
    for i, ch in enumerate(text):
        idx = ALPHABET.index(ch)
        bits = format(idx, '05b')
        print(f"  Буква '{ch}' → индекс {idx:2d} → 5 бит: {bits}")
        result += bits
    print(f"  Итоговая битовая строка: {result}")
    print(f"  Длина: {len(result)} бит")
    return result


def bits_to_text(bits: str) -> str:
    """Конвертирует 5-битные коды обратно в русские буквы."""
    print(f"\n--- ПРЕОБРАЗОВАНИЕ БИТОВ В ТЕКСТ ---")
    chunks = [bits[i:i + 5] for i in range(0, len(bits), 5) if len(bits[i:i + 5]) == 5]
    result = ""
    for i, chunk in enumerate(chunks):
        idx = int(chunk, 2)
        letter = ALPHABET[idx]
        print(f"  Блок {i + 1}: {chunk} (биты) → {idx:2d} (индекс) → буква '{letter}'")
        result += letter
    print(f"  Восстановленный текст: {result}")
    return result


def normalize_text(text: str) -> str:
    """Подготовка текста: нижний регистр, замена ё, знаков и пробелов."""
    print(f"\n--- НОРМАЛИЗАЦИЯ ТЕКСТА ---")
    print(f"  Исходный текст: {text}")

    text = text.lower()
    print(f"  Нижний регистр: {text}")

    text = text.replace('ё', 'е')
    print(f"  Замена ё → е: {text}")

    for punct, repl in PUNCT_MAP.items():
        if punct in text:
            old_text = text
            text = text.replace(punct, repl)
            if old_text != text:
                print(f"  Замена '{punct}' → '{repl}': {text}")

    print(f"  Нормализованный текст: {text}")
    return text


def denormalize_text(text: str) -> str:
    """Восстановление знаков препинания и пробелов."""
    print(f"\n--- ВОССТАНОВЛЕНИЕ ЗНАКОВ ---")
    print(f"  Текст после расшифровки: {text}")

    for word, punct in REV_PUNCT_MAP.items():
        if word in text:
            old_text = text
            text = text.replace(word, punct)
            if old_text != text:
                print(f"  Замена '{word}' → '{punct}': {text}")

    print(f"  Восстановленный текст: {text}")
    return text


# =====================================================================
#   РАБОТА С КЛЮЧОМ И КАДРОМ
# =====================================================================
def get_key_bits() -> str:
    """Запрашивает ключ (только 8 русских букв) и возвращает 64 бита."""
    print("\n" + "=" * 70)
    print("ВВОД КЛЮЧА")
    print("=" * 70)

    key_word = input("Ключ (8 русских букв): ").strip().lower()

    # Проверка
    invalid = [ch for ch in key_word if ch not in ALPHABET]
    if invalid:
        print(f"Ошибка: недопустимые символы: {invalid}")
        sys.exit(1)

    if len(key_word) < 8:
        print("Ошибка: минимум 8 букв")
        sys.exit(1)

    key_word = key_word[:8]
    print(f"\nКлючевое слово: {key_word}")

    # Показываем преобразование в биты
    print("\nПреобразование в биты (UTF-8):")
    key_bits = ""
    for i, ch in enumerate(key_word):
        byte = ch.encode('utf-8')
        bits = ''.join(format(b, '08b') for b in byte)
        print(f"  Буква '{ch}' → байт(ы) {list(byte)} → биты: {bits}")
        key_bits += bits

    key_bits = key_bits[:64]
    print(f"\nИтоговый 64-битный ключ: {key_bits}")
    return key_bits


def get_frame_number() -> int:
    """Запрашивает номер кадра."""
    try:
        frame = int(input("Номер кадра (по умолчанию 0): ").strip() or "0")
        print(f"  Выбран номер кадра: {frame} (двоичный: {format(frame, '022b')})")
        return frame
    except ValueError:
        print("  Используется номер 0")
        return 0


# =====================================================================
#   ГЕНЕРАТОР A5/1
# =====================================================================
def generate_gamma(key_bits: str, frame_num: int) -> list:
    """Генерирует 114 бит гаммы для ключа и номера кадра с подробным выводом."""
    print(f"\n{'=' * 70}")
    print(f"ГЕНЕРАЦИЯ ГАММЫ ДЛЯ КАДРА {frame_num}")
    print(f"{'=' * 70}")

    # Инициализация регистров
    r1 = [0] * 19
    r2 = [0] * 22
    r3 = [0] * 23

    print(f"\n1. НАЧАЛЬНОЕ СОСТОЯНИЕ РЕГИСТРОВ:")
    print(f"   R1 (19 бит): {r1}")
    print(f"   R2 (22 бита): {r2}")
    print(f"   R3 (23 бита): {r3}")

    # Загрузка ключа (64 такта)
    print(f"\n2. ЗАГРУЗКА КЛЮЧА (64 такта):")
    for i in range(64):
        bit = int(key_bits[i])
        print(f"\n   Такт {i + 1:2d}: ключевой бит = {bit}")

        old_r1 = r1.copy()
        old_r2 = r2.copy()
        old_r3 = r3.copy()

        new_r1 = r1[0] ^ bit
        new_r2 = r2[0] ^ bit
        new_r3 = r3[0] ^ bit

        r1 = r1[1:] + [new_r1]
        r2 = r2[1:] + [new_r2]
        r3 = r3[1:] + [new_r3]

        print(f"   R1: {old_r1} → {r1} (новый бит: {new_r1})")
        print(f"   R2: {old_r2} → {r2} (новый бит: {new_r2})")
        print(f"   R3: {old_r3} → {r3} (новый бит: {new_r3})")

    # Загрузка номера кадра (22 такта)
    print(f"\n3. ЗАГРУЗКА НОМЕРА КАДРА (22 такта):")
    frame_bits = format(frame_num, '022b')
    print(f"   Номер кадра в двоичном виде: {frame_bits}")

    for i in range(22):
        bit = int(frame_bits[i])
        print(f"\n   Такт {i + 1:2d}: бит кадра = {bit}")

        old_r1 = r1.copy()
        old_r2 = r2.copy()
        old_r3 = r3.copy()

        new_r1 = r1[0] ^ bit
        new_r2 = r2[0] ^ bit
        new_r3 = r3[0] ^ bit

        r1 = r1[1:] + [new_r1]
        r2 = r2[1:] + [new_r2]
        r3 = r3[1:] + [new_r3]

        print(f"   R1: {old_r1} → {r1}")
        print(f"   R2: {old_r2} → {r2}")
        print(f"   R3: {old_r3} → {r3}")

    # Перемешивание (100 тактов)
    print(f"\n4. ПЕРЕМЕШИВАНИЕ (100 тактов):")
    for step in range(100):
        maj_sum = r1[8] + r2[10] + r3[10]
        majority = 1 if maj_sum > 1 else 0

        if step < 5 or step >= 95:
            print(f"\n   Такт {step + 1:3d}: мажоритарный бит = {majority} (из {r1[8]}+{r2[10]}+{r3[10]}={maj_sum})")
            old_r1 = r1.copy()
            old_r2 = r2.copy()
            old_r3 = r3.copy()

            if r1[8] == majority:
                new_bit = r1[13] ^ r1[16] ^ r1[17] ^ r1[18]
                r1 = r1[1:] + [new_bit]
                print(f"   R1 тактируется: новый бит = {new_bit}")
            else:
                r1 = r1[1:] + [r1[18]]
                print(f"   R1 не тактируется (простой сдвиг)")

            if r2[10] == majority:
                new_bit = r2[20] ^ r2[21]
                r2 = r2[1:] + [new_bit]
                print(f"   R2 тактируется: новый бит = {new_bit}")
            else:
                r2 = r2[1:] + [r2[21]]
                print(f"   R2 не тактируется (простой сдвиг)")

            if r3[10] == majority:
                new_bit = r3[7] ^ r3[20] ^ r3[21] ^ r3[22]
                r3 = r3[1:] + [new_bit]
                print(f"   R3 тактируется: новый бит = {new_bit}")
            else:
                r3 = r3[1:] + [r3[22]]
                print(f"   R3 не тактируется (простой сдвиг)")

            print(f"   R1: {old_r1} → {r1}")
            print(f"   R2: {old_r2} → {r2}")
            print(f"   R3: {old_r3} → {r3}")
        else:
            if r1[8] == majority:
                r1 = r1[1:] + [r1[13] ^ r1[16] ^ r1[17] ^ r1[18]]
            else:
                r1 = r1[1:] + [r1[18]]

            if r2[10] == majority:
                r2 = r2[1:] + [r2[20] ^ r2[21]]
            else:
                r2 = r2[1:] + [r2[21]]

            if r3[10] == majority:
                r3 = r3[1:] + [r3[7] ^ r3[20] ^ r3[21] ^ r3[22]]
            else:
                r3 = r3[1:] + [r3[22]]

    # Генерация 114 бит гаммы
    print(f"\n5. ГЕНЕРАЦИЯ 114 БИТ ГАММЫ:")
    gamma = []

    for i in range(114):
        maj_sum = r1[8] + r2[10] + r3[10]
        majority = 1 if maj_sum > 1 else 0
        out_bit = r1[18] ^ r2[21] ^ r3[22]
        gamma.append(out_bit)

        if i < 10 or i >= 104:
            print(f"\n   Бит {i + 1:3d}: выходной бит = {out_bit} (R1[18]={r1[18]} ⊕ R2[21]={r2[21]} ⊕ R3[22]={r3[22]})")
            print(f"      мажоритарный бит = {majority} (из {r1[8]}+{r2[10]}+{r3[10]}={maj_sum})")
            old_r1 = r1.copy()
            old_r2 = r2.copy()
            old_r3 = r3.copy()

            if r1[8] == majority:
                new_bit = r1[13] ^ r1[16] ^ r1[17] ^ r1[18]
                r1 = r1[1:] + [new_bit]
                print(f"      R1 тактируется: новый бит = {new_bit}")
            else:
                r1 = r1[1:] + [r1[18]]
                print(f"      R1 не тактируется")

            if r2[10] == majority:
                new_bit = r2[20] ^ r2[21]
                r2 = r2[1:] + [new_bit]
                print(f"      R2 тактируется: новый бит = {new_bit}")
            else:
                r2 = r2[1:] + [r2[21]]
                print(f"      R2 не тактируется")

            if r3[10] == majority:
                new_bit = r3[7] ^ r3[20] ^ r3[21] ^ r3[22]
                r3 = r3[1:] + [new_bit]
                print(f"      R3 тактируется: новый бит = {new_bit}")
            else:
                r3 = r3[1:] + [r3[22]]
                print(f"      R3 не тактируется")

            print(f"      R1: {old_r1} → {r1}")
            print(f"      R2: {old_r2} → {r2}")
            print(f"      R3: {old_r3} → {r3}")
        else:
            if r1[8] == majority:
                r1 = r1[1:] + [r1[13] ^ r1[16] ^ r1[17] ^ r1[18]]
            else:
                r1 = r1[1:] + [r1[18]]

            if r2[10] == majority:
                r2 = r2[1:] + [r2[20] ^ r2[21]]
            else:
                r2 = r2[1:] + [r2[21]]

            if r3[10] == majority:
                r3 = r3[1:] + [r3[7] ^ r3[20] ^ r3[21] ^ r3[22]]
            else:
                r3 = r3[1:] + [r3[22]]

    gamma_str = ''.join(str(bit) for bit in gamma)
    print(f"\n   Итоговая гамма (первые 30 бит): {gamma_str[:30]}...")
    print(f"   Итоговая гамма (последние 30 бит): ...{gamma_str[-30:]}")
    print(f"   Полная длина гаммы: {len(gamma)} бит")

    return gamma


# =====================================================================
#   ОСНОВНОЙ ШИФРАТОР С ВЫВОДОМ
# =====================================================================
def encrypt_data(data_bits: str, key_bits: str, start_frame: int = 0) -> str:
    """Шифрует битовую строку с подробным выводом."""
    print(f"\n{'=' * 70}")
    print("ПРОЦЕСС ШИФРОВАНИЯ")
    print(f"{'=' * 70}")
    print(f"Исходные данные (биты): {data_bits}")
    print(f"Длина данных: {len(data_bits)} бит")
    print(f"Количество кадров: {(len(data_bits) + 113) // 114}")

    result = ""
    frame = start_frame

    for i in range(0, len(data_bits), 114):
        block = data_bits[i:i + 114]
        print(f"\n{'─' * 70}")
        print(f"КАДР {frame}")
        print(f"{'─' * 70}")
        print(f"Блок данных ({len(block)} бит): {block}")

        gamma = generate_gamma(key_bits, frame)

        print(f"\nПобитовый XOR:")
        xored = ""
        for j in range(len(block)):
            xor = int(block[j]) ^ gamma[j]
            xored += str(xor)
            if j < 10:  # Показываем первые 10 операций
                print(f"  Бит {j + 1:2d}: {block[j]} ⊕ {gamma[j]} = {xor}")

        result += xored
        print(f"\nЗашифрованный блок: {xored}")
        frame += 1

    print(f"\n{'─' * 70}")
    print(f"ИТОГОВЫЙ ЗАШИФРОВАННЫЙ ТЕКСТ (биты): {result}")
    return result


def decrypt_data(cipher_bits: str, key_bits: str, start_frame: int = 0) -> str:
    """Дешифрует битовую строку (аналогично шифрованию)."""
    print(f"\n{'=' * 70}")
    print("ПРОЦЕСС ДЕШИФРОВАНИЯ")
    print(f"{'=' * 70}")
    return encrypt_data(cipher_bits, key_bits, start_frame)


def encrypt_text(plaintext: str, key_bits: str, start_frame: int = 0) -> str:
    """Полное шифрование текста."""
    print(f"\n{'=' * 70}")
    print("ПОЛНЫЙ ЦИКЛ ШИФРОВАНИЯ")
    print(f"{'=' * 70}")

    normalized = normalize_text(plaintext)
    data_bits = text_to_bits(normalized)
    cipher_bits = encrypt_data(data_bits, key_bits, start_frame)

    formatted = ' '.join(cipher_bits[i:i + 5] for i in range(0, len(cipher_bits), 5))
    print(f"\n{'=' * 70}")
    print(f"ИТОГОВЫЙ РЕЗУЛЬТАТ (группы по 5 бит):")
    print(formatted)

    return formatted


def decrypt_text(ciphertext: str, key_bits: str, start_frame: int = 0) -> str:
    """Полное дешифрование текста."""
    print(f"\n{'=' * 70}")
    print("ПОЛНЫЙ ЦИКЛ ДЕШИФРОВАНИЯ")
    print(f"{'=' * 70}")

    bits = ciphertext.replace(' ', '')
    print(f"Входные биты (без пробелов): {bits}")

    plain_bits = decrypt_data(bits, key_bits, start_frame)
    recovered_text = bits_to_text(plain_bits)
    final_text = denormalize_text(recovered_text)

    print(f"\n{'=' * 70}")
    print(f"ИТОГОВЫЙ РАСШИФРОВАННЫЙ ТЕКСТ:")
    print(final_text)

    return final_text


# =====================================================================
#   ИНТЕРФЕЙС / ГЛАВНОЕ МЕНЮ
# =====================================================================
def main():
    while True:
        print("\n" + "="*50)
        print("ПОТОЧНЫЙ ШИФР A5/1")
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Выход")
        print("="*50)

        choice = input("Выберите пункт меню: ")

        if choice in ['1', '2']:
            text = input("Введите текст: ").strip()
            key_bits = get_key_bits()
            frame_num = get_frame_number()
            
            if choice == '1':
                encrypt_text(text, key_bits, frame_num)
            elif choice == '2':
                decrypt_text(text, key_bits, frame_num)
                
        elif choice == '3':
            print("Работа завершена. До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")
            continue

        cont = input("\nПродолжить выполнение всей программы? (да/нет): ").lower()
        if cont not in ['да', 'д', 'yes', 'y']:
            print("Работа завершена.")
            break

if __name__ == "__main__":
    main()