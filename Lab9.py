import os
import random  # Для автоматической генерации K
import math    # Для проверки НОД (gcd)

# =====================================================================
#   АЛФАВИТ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =====================================================================
ALPHABET = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"  # 31 буква: А=1, ..., Я=31

def get_char_code(char):
    """
    Возвращает код символа в алфавите: А=1, Б=2, ..., Я=31.
    Ё заменяется на Е, Й заменяется на И.
    Символы вне алфавита возвращают 0.
    """
    char = char.upper()
    if char == 'Ё': char = 'Е'
    if char == 'Й': char = 'И'
    if char in ALPHABET:
        return ALPHABET.index(char) + 1
    return 0

def calculate_hash(text, p):
    """
    Упрощённая хеш-функция квадратичной свертки:
        h₀ = 0
        hᵢ = (hᵢ₋₁ + Mᵢ)² mod p
    Возвращает хеш в диапазоне [0, p-1].
    """
    h = 0
    for char in text:
        m_i = get_char_code(char)
        if m_i > 0:
            h = (h + m_i) ** 2 % p
    return h

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x, y = extended_gcd(b % a, a)
    return gcd, y - (b // a) * x, x

def mod_inverse(a, m):
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1:
        raise Exception('Обратного элемента не существует')
    return x % m

# =====================================================================
#   АЛГОРИТМ RSA
# =====================================================================
def rsa_generate_keys():
    print("\n--- Генерация ключей RSA ---")
    while True:
        try:
            P = int(input("Введите простое число P: "))
            Q = int(input("Введите простое число Q: "))
            N = P * Q
            if N <= 32:
                print("ОШИБКА: Модуль N должен быть больше 32!")
                continue
            break
        except ValueError:
            print("ОШИБКА: Введите целые числа.")
            
    phi = (P - 1) * (Q - 1)
    while True:
        try:
            E = int(input(f"Выберите открытый ключ E (1 < E < {phi}, взаимно простое с {phi}): "))
            D = mod_inverse(E, phi)
            if E == D:
                print("ОШИБКА: E совпал с D. Выберите другое число.")
                continue
            break
        except ValueError:
            print("ОШИБКА: Введите целое число.")
        except Exception:
            print("ОШИБКА: E и phi(N) не взаимно простые.")
            
    return (E, N), (D, N)

def rsa_sign(text, D, N):
    m = calculate_hash(text, N)
    print(f"Хэш-код сообщения m = {m}")
    S = pow(m, D, N)
    print(f"Электронная цифровая подпись S = {S}")
    return S

def rsa_verify(text, S, E, N):
    m = calculate_hash(text, N)
    m_decrypted = pow(S, E, N)
    if m == m_decrypted:
        print(f"✅ Подпись RSA ВЕРНА. H(text) = {m}, S^E mod N = {m_decrypted}")
    else:
        print(f"❌ Подпись RSA НЕВЕРНА. H(text) = {m}, S^E mod N = {m_decrypted}")
    return m == m_decrypted

# =====================================================================
#   АЛГОРИТМ ЭЛЬ-ГАМАЛЯ (ELGAMAL)
# =====================================================================
def elgamal_generate_keys():
    print("\n--- Генерация ключей ElGamal ---")
    while True:
        try:
            P = int(input("Введите простое число P (P > 32): "))
            if P <= 32:
                print("ОШИБКА: P должен быть > 32!")
                continue
            break
        except ValueError:
            print("ОШИБКА: Введите целое число.")
        
    G = int(input(f"Введите целое число G (1 < G < {P}): "))
    
    while True:
        try:
            X = int(input(f"Введите секретный ключ X (1 < X < {P-1}): "))
            Y = pow(G, X, P)
            if Y == X:
                print(f"ОШИБКА: Y совпал с X ({X}). Выберите другой X.")
                continue
            break
        except ValueError:
            print("ОШИБКА: Введите целое число.")
            
    return (Y, G, P), X

def elgamal_sign(text, X, P, G):
    """
    Подписание сообщения алгоритмом ElGamal с АВТОМАТИЧЕСКОЙ генерацией K.
    """
    m = calculate_hash(text, P)
    print(f"Хэш-код сообщения m = {m}")
    
    # --- АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ K ---
    # K должно быть в диапазоне (1, P-1) и взаимно просто с P-1
    phi = P - 1
    while True:
        # Генерируем случайное число от 2 до P-2
        K = random.randint(2, P - 2)
        # Проверяем условие gcd(K, P-1) == 1
        if math.gcd(K, phi) == 1:
            break
    
    print(f"🎲 Автоматически сгенерированное случайное число K = {K}")
    # ----------------------------------
    
    try:
        k_inv = mod_inverse(K, P - 1)
    except Exception as e:
        print(f"Ошибка вычисления обратного элемента для K={K}: {e}")
        return None, None

    a = pow(G, K, P)
    # Формула: b = K^-1 * (m - X*a) mod (P-1)
    b = (k_inv * (m - X * a)) % (P - 1)
    
    print(f"Цифровая подпись S = (a: {a}, b: {b})")
    return a, b

def elgamal_verify(text, a, b, Y, G, P):
    """
    Проверка подписи ElGamal:
        Левая часть:  L = G^m mod P
        Правая часть: R = (Y^a * a^b) mod P
    """
    m = calculate_hash(text, P)
    left = pow(G, m, P)
    right = (pow(Y, a, P) * pow(a, b, P)) % P
    
    if left == right:
        print(f"✅ Подпись ElGamal ВЕРНА. G^m mod P = {left}, Y^a * a^b mod P = {right}")
    else:
        print(f"❌ Подпись ElGamal НЕВЕРНА. G^m mod P = {left}, Y^a * a^b mod P = {right}")
    return left == right

# =====================================================================
#   ОСНОВНОЙ ФУНКЦИОНАЛ (Файлы и Интерфейс)
# =====================================================================
def read_text_from_file():
    if not os.path.exists("input.txt"):
        print("Файл input.txt не найден.")
        return None
    with open("input.txt", 'r', encoding='utf-8') as f:
        return f.read().strip()

def main():
    while True:
        print("\n=== МЕНЮ ===")
        print("1. Создание подписи RSA")
        print("2. Создание подписи ElGamal (Авто-K)")
        print("3. Проверка подписи RSA")
        print("4. Проверка подписи ElGamal")
        print("5. Выход")
        choice = input("Выбор: ")
        
        if choice in ['1', '2', '3', '4']:
            text = read_text_from_file()
            if not text:
                print("Текст не загружен. Создайте файл input.txt и повторите попытку.")
                continue
            
            try:
                if choice == '1':
                    pub, priv = rsa_generate_keys()
                    rsa_sign(text, priv[0], priv[1])
                    print(f"\n Для проверки используйте: S, E={pub[0]}, N={pub[1]}")
                    
                elif choice == '2':
                    pub, priv_x = elgamal_generate_keys()
                    a, b = elgamal_sign(text, priv_x, pub[2], pub[1])
                    if a is not None and b is not None:
                        print(f"\n💡 Для проверки используйте: a={a}, b={b}, Y={pub[0]}, G={pub[1]}, P={pub[2]}")
                    
                elif choice == '3':
                    print("\n--- Проверка подписи RSA ---")
                    S = int(input("Введите подпись S: "))
                    E = int(input("Введите открытый ключ E: "))
                    N = int(input("Введите модуль N: "))
                    rsa_verify(text, S, E, N)
                    
                elif choice == '4':
                    print("\n--- Проверка подписи ElGamal ---")
                    a = int(input("Введите часть подписи a: "))
                    b = int(input("Введите часть подписи b: "))
                    Y = int(input("Введите открытый ключ Y: "))
                    G = int(input("Введите параметр G: "))
                    P = int(input("Введите простое число P: "))
                    elgamal_verify(text, a, b, Y, G, P)
                    
            except ValueError:
                print("ОШИБКА: Введите корректные целые числа.")
                
        elif choice == '5':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()