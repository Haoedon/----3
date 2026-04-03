import math
import random

# =====================================================================
#   КОНСТАНТЫ И АЛФАВИТ (1-32)
# =====================================================================
ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ALPHABET_SIZE = len(ALPHABET) # 32

# =====================================================================
#   МАТЕМАТИЧЕСКИЙ ДВИЖОК
# =====================================================================
def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    gcd, x, y = extended_gcd(a, m)
    if gcd != 1: return None
    return x % m

# =====================================================================
#   ПРЕОБРАЗОВАНИЕ ТЕКСТА
# =====================================================================
def text_to_ints(text):
    text = text.lower().replace("ё", "е")
    print(f"\n--- ПРЕОБРАЗОВАНИЕ В ИНДЕКСЫ (а=1, ..., к=11) ---")
    ints = []
    for c in text:
        if c in ALPHABET:
            idx = ALPHABET.index(c) + 1
            ints.append(idx)
            print(f"  '{c}' -> {idx}")
    return ints

def ints_to_text(ints):
    return "".join([ALPHABET[i - 1] for i in ints if 1 <= i <= 32])

# =====================================================================
#   1. АЛГОРИТМ RSA
# =====================================================================
def rsa_menu():
    print(f"\n{'='*20} RSA (Асимметричный) {'='*20}")
    choice = input("1. Зашифровать\n2. Расшифровать\nВыбор: ")
    
    if choice == '1':
        p = int(input("Введите простое P: "))
        q = int(input("Введите простое Q: "))
        n = p * q
        phi = (p - 1) * (q - 1)
        
        if n <= ALPHABET_SIZE:
            print(f"Ошибка: Модуль N={n} должен быть больше {ALPHABET_SIZE}!")
            return
            
        while True:
            e = int(input(f"Введите открытую экспоненту E (1 < E < {phi}): "))
            if math.gcd(e, phi) != 1:
                print("E должно быть взаимно простым с φ(N)!")
                continue
            d = mod_inverse(e, phi)
            if d == e:
                print(f"Критическая ошибка: d ({d}) совпадает с e ({e}). Выберите другое E!")
                continue
            break
            
        print(f"Ключи: Открытый {{E:{e}, N:{n}}}, Секретный {{D:{d}, N:{n}}}")
        m_ints = text_to_ints(input("Сообщение: "))
        cipher = [pow(m, e, n) for m in m_ints]
        print(f"Шифртекст: {' '.join(map(str, cipher))}")
        
    else:
        n = int(input("Введите N: "))
        d = int(input("Введите секретный ключ D: "))
        data = list(map(int, input("Шифртекст (через пробел): ").split()))
        res = [pow(c, d, n) for c in data]
        print(f"Результат: {ints_to_text(res)}")

# =====================================================================
#   2. АЛГОРИТМ ELGAMAL
# =====================================================================
def elgamal_menu():
    print(f"\n{'='*20} ELGAMAL {'='*20}")
    choice = input("1. Зашифровать\n2. Расшифровать\nВыбор: ")
    
    if choice == '1':
        p = int(input(f"Введите простое P (> {ALPHABET_SIZE}): "))
        if p <= ALPHABET_SIZE: return
        g = int(input(f"Введите g (1 < g < {p}): "))
        x = int(input(f"Введите секретный x: "))
        y = pow(g, x, p)
        
        m_ints = text_to_ints(input("Сообщение: "))
        cipher = []
        print("\n--- ПРОЦЕСС ШИФРОВАНИЯ (с рандомизаторами) ---")
        for m in m_ints:
            while True:
                k = random.randint(2, p - 2)
                if math.gcd(k, p - 1) == 1: break
            a = pow(g, k, p)
            b = (pow(y, k, p) * m) % p
            cipher.append(f"{a} {b}")
            print(f"  Символ (индекс {m}): выбран k={k} -> пара (a={a}, b={b})")
        print(f"\nИтоговый шифртекст: {' '.join(cipher)}")
        
    else:
        p = int(input("Введите P: "))
        x = int(input("Введите секретный x: "))
        data = list(map(int, input("Шифртекст (пары a b): ").split()))
        res = []
        for i in range(0, len(data), 2):
            a, b = data[i], data[i+1]
            # M = b * (a^x)^-1 mod p
            ax_inv = mod_inverse(pow(a, x, p), p)
            res.append((b * ax_inv) % p)
        print(f"Результат: {ints_to_text(res)}")

# =====================================================================
#   3. ECC (НА ОСНОВЕ АБСЦИССЫ) - ИСПРАВЛЕННЫЙ
# =====================================================================
def ec_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    
    # Случай, когда точки дают бесконечность (P = -Q)
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    
    # Вычисление наклона m
    if P == Q:
        num = (3 * x1**2 + a) % p
        den = (2 * y1) % p
    else:
        num = (y2 - y1) % p
        den = (x2 - x1) % p
    
    inv = mod_inverse(den, p)
    if inv is None:
        return None  # Точка ушла в бесконечность
        
    m = (num * inv) % p
    x3 = (m**2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P, a, p):
    """Быстрое возведение в степень (Binary Ladder) вместо цикла for"""
    res = None
    temp = P
    while k > 0:
        if k % 2 == 1:
            res = ec_add(res, temp, a, p)
        temp = ec_add(temp, temp, a, p)
        k //= 2
    return res

def ecc_menu():
    print(f"\n{'='*20} ECC (Абсцисса) - Автоматический расчет q {'='*20}")
    
    # Ввод параметров кривой
    try:
        p = int(input("Введите простое число p (модуль поля): "))
        a = int(input("Введите коэффициент 'a' кривой: "))
        gx = int(input("Введите координату X базовой точки G: "))
        gy = int(input("Введите координату Y базовой точки G: "))
        G = (gx, gy)
    except ValueError:
        print("Ошибка ввода: параметры должны быть целыми числами.")
        return

    # Автоматическое вычисление порядка q
    print("\nВычисление порядка подгруппы q...")
    q = 1
    while True:
        pt = ec_mul(q, G, a, p)
        if pt is None:  # Точка ушла в бесконечность
            break
        q += 1
        # Защита от бесконечного цикла (по теореме Хассе порядок не может сильно превышать p)
        if q > p + int(2 * math.sqrt(p)) + 1: 
            print("Ошибка: Не удалось найти порядок q. Убедитесь, что точка G действительно лежит на кривой.")
            return
            
    print(f"Порядок базовой точки G (q) успешно вычислен: {q}")

    choice = input("\n1. Зашифровать\n2. Расшифровать\nВыбор: ")
    
    if choice == '1':
        cb = int(input(f"Введите секретный ключ получателя (1-{q-1}): "))
        
        # Вычисляем открытый ключ получателя Db = cb * G
        db = ec_mul(cb, G, a, p)
        if db is None:
            print("Ошибка: Ключ привел к бесконечной точке. Выберите другое значение.")
            return
            
        print(f"Вычислен открытый ключ получателя (Db): {db}")
        
        m_text = input("Введите сообщение для шифрования: ")
        m_ints = text_to_ints(m_text)
        cipher = []
        
        print("\n--- ПРОЦЕСС ШИФРОВАНИЯ ---")
        for m in m_ints:
            # Генерация случайного k
            k = random.randint(1, q - 1)
            
            # R = k * G
            R = ec_mul(k, G, a, p)
            # P_pt = k * Db
            P_pt = ec_mul(k, db, a, p)
            
            # Проверка, чтобы точка не ушла в бесконечность и абсцисса не была равна 0
            while P_pt is None or P_pt[0] == 0:
                k = random.randint(1, q - 1)
                R = ec_mul(k, G, a, p)
                P_pt = ec_mul(k, db, a, p)
            
            # e = (m * x) mod p
            e = (m * P_pt[0]) % p
            cipher.append(f"{R[0]} {R[1]} {e}")
            print(f"  Символ M={m}: выбрано k={k} -> R=({R[0]},{R[1]}), P_x={P_pt[0]}, e={e}")
            
        print(f"\nИтоговый шифртекст (Rx Ry e): {' '.join(cipher)}")
        
    elif choice == '2':
        cb = int(input("Введите ваш секретный ключ cb: "))
        
        try:
            data = list(map(int, input("Введите шифртекст (тройки чисел Rx Ry e через пробел): ").split()))
        except ValueError:
            print("Ошибка ввода: шифртекст должен состоять из чисел.")
            return
            
        if len(data) % 3 != 0:
            print("Ошибка: Количество чисел в шифртексте должно быть кратно 3 (Rx, Ry, e).")
            return
            
        res_ints = []
        print("\n--- ПРОЦЕСС РАСШИФРОВКИ ---")
        for i in range(0, len(data), 3):
            R = (data[i], data[i+1])
            e = data[i+2]
            
            # Q = cb * R
            Q = ec_mul(cb, R, a, p)
            
            if Q is None or Q[0] == 0:
                print(f"Ошибка при расшифровке блока {i//3 + 1}: точка ушла в бесконечность или x=0.")
                res_ints.append(0) # Заглушка, чтобы не ломать весь текст
                continue
                
            # m = e * x^-1 mod p
            inv_x = mod_inverse(Q[0], p)
            if inv_x is None:
                print(f"Ошибка: невозможно найти обратный элемент для x={Q[0]}")
                continue
                
            m_decrypted = (e * inv_x) % p
            res_ints.append(m_decrypted)
            print(f"  Блок {i//3 + 1}: Q=({Q[0]},{Q[1]}), x^-1={inv_x}, m'={m_decrypted}")
            
        print(f"\nРезультат (текст): {ints_to_text(res_ints)}")
    else:
        print("Неверный выбор.")
# =====================================================================
#   ГЛАВНОЕ МЕНЮ
# =====================================================================
def main():
    while True:
        print("\n" + "="*50)
        print("АСИММЕТРИЧНЫЕ КРИПТОСИСТЕМЫ (КИРИЛЛИЦА 1-32)")
        print("1. RSA")
        print("2. ElGamal")
        print("3. ECC (Абсцисса)")
        print("4. Выход")
        print("="*50)
        choice = input("Выберите алгоритм: ")
        
        if choice == '1': rsa_menu()
        elif choice == '2': elgamal_menu()
        elif choice == '3': ecc_menu()
        elif choice == '4': break
        else: print("Ошибка выбора!")

if __name__ == "__main__":
    main()