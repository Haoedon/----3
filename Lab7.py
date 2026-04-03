import sys
import struct

=====================================================================
ТАБЛИЦЫ И КОНСТАНТЫ (МАГМА)
=====================================================================
PI_MAGMA = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2],
]

=====================================================================
РЕАЛИЗАЦИЯ МАГМА (ГОСТ Р 34.12-2015)
=====================================================================
def magma_f(node, key_part):
    temp = (node + key_part) % (2**32)
    res = 0
    for i in range(8):
        nibble = (temp >> (4 * i)) & 0x0F
        res |= (PI_MAGMA[i][nibble] << (4 * i))
    return ((res << 11) | (res >> 21)) & 0xFFFFFFFF

def magma_round(l, r, key_part):
    return r, l ^ magma_f(r, key_part)

def magma_process(data, key, encrypt=True):
    subkeys = [struct.unpack("<I", key[i:i+4])[0] for i in range(0, 32, 4)]
    if encrypt:
        round_keys = subkeys * 3 + subkeys[::-1]
    else:
        round_keys = subkeys + subkeys[::-1] * 3
    result = bytearray()
    for i in range(0, len(data), 8):
        l, r = struct.unpack("<II", data[i:i+8])
        for j in range(31):
            l, r = magma_round(l, r, round_keys[j])
        _, res = magma_round(l, r, round_keys[31])
        result += struct.pack("<II", res, _)
    return bytes(result)

=====================================================================
РЕАЛИЗАЦИЯ AES (FIPS-197) — из файла aes (1).py
=====================================================================
SBOX = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
    [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
    [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
    [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
    [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
    [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
    [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
    [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
    [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
    [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
    [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
]

INV_SBOX = [
    [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb],
    [0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb],
    [0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e],
    [0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25],
    [0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92],
    [0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84],
    [0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06],
    [0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b],
    [0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73],
    [0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e],
    [0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b],
    [0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4],
    [0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f],
    [0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef],
    [0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61],
    [0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]
]

Rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a]

def sub_byte(b):
    return SBOX[b >> 4][b & 0x0F]

def inv_sub_byte(b):
    return INV_SBOX[b >> 4][b & 0x0F]

def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = sub_byte(state[i][j])

def inv_sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = inv_sub_byte(state[i][j])

def shift_rows(state):
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][1], state[1][2], state[1][3], state[1][0]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][3], state[3][0], state[3][1], state[3][2]

def inv_shift_rows(state):
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][3], state[1][0], state[1][1], state[1][2]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][1], state[3][2], state[3][3], state[3][0]

def xtime(b):
    if b & 0x80:
        return ((b << 1) & 0xFF) ^ 0x1B
    else:
        return (b << 1) & 0xFF

def mix_columns(state):
    for c in range(4):
        s0 = state[0][c]
        s1 = state[1][c]
        s2 = state[2][c]
        s3 = state[3][c]
        state[0][c] = xtime(s0) ^ (xtime(s1) ^ s1) ^ s2 ^ s3
        state[1][c] = s0 ^ xtime(s1) ^ (xtime(s2) ^ s2) ^ s3
        state[2][c] = s0 ^ s1 ^ xtime(s2) ^ (xtime(s3) ^ s3)
        state[3][c] = (xtime(s0) ^ s0) ^ s1 ^ s2 ^ xtime(s3)

def inv_mix_columns(state):
    for c in range(4):
        s0 = state[0][c]
        s1 = state[1][c]
        s2 = state[2][c]
        s3 = state[3][c]
        state[0][c] = mul(0x0e, s0) ^ mul(0x0b, s1) ^ mul(0x0d, s2) ^ mul(0x09, s3)
        state[1][c] = mul(0x09, s0) ^ mul(0x0e, s1) ^ mul(0x0b, s2) ^ mul(0x0d, s3)
        state[2][c] = mul(0x0d, s0) ^ mul(0x09, s1) ^ mul(0x0e, s2) ^ mul(0x0b, s3)
        state[3][c] = mul(0x0b, s0) ^ mul(0x0d, s1) ^ mul(0x09, s2) ^ mul(0x0e, s3)

def mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a = xtime(a)
        b >>= 1
    return result

def add_round_key(state, round_key):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= round_key[i][j]

def key_expansion(key):
    Nk = len(key) // 4
    Nr = Nk + 6
    w = []
    for i in range(Nk):
        w.append(int.from_bytes(key[i*4:(i+1)*4], 'big'))
    for i in range(Nk, 4*(Nr+1)):
        temp = w[i-1]
        if i % Nk == 0:
            temp = ((temp << 8) & 0xFFFFFFFF) | (temp >> 24)
            temp = (sub_byte((temp >> 24) & 0xFF) << 24) | \
                   (sub_byte((temp >> 16) & 0xFF) << 16) | \
                   (sub_byte((temp >> 8) & 0xFF) << 8) | \
                   sub_byte(temp & 0xFF)
            temp ^= (Rcon[i//Nk - 1] << 24)
        elif Nk > 6 and i % Nk == 4:
            temp = (sub_byte((temp >> 24) & 0xFF) << 24) | \
                   (sub_byte((temp >> 16) & 0xFF) << 16) | \
                   (sub_byte((temp >> 8) & 0xFF) << 8) | \
                   sub_byte(temp & 0xFF)
        w.append(w[i-Nk] ^ temp)
    round_keys = []
    for round in range(Nr+1):
        key_matrix = [[0]*4 for _ in range(4)]
        for col in range(4):
            word = w[round*4 + col]
            key_matrix[0][col] = (word >> 24) & 0xFF
            key_matrix[1][col] = (word >> 16) & 0xFF
            key_matrix[2][col] = (word >> 8) & 0xFF
            key_matrix[3][col] = word & 0xFF
        round_keys.append(key_matrix)
    return round_keys

def aes_encrypt_block(block: bytes, round_keys: list) -> bytes:
    if len(block) != 16:
        raise ValueError("Блок должен быть 16 байт")
    state = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i + 4*j]
    Nr = len(round_keys) - 1
    add_round_key(state, round_keys[0])
    for round in range(1, Nr):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, round_keys[round])
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, round_keys[Nr])
    output = bytearray(16)
    for i in range(4):
        for j in range(4):
            output[i + 4*j] = state[i][j]
    return bytes(output)

def aes_decrypt_block(block: bytes, round_keys: list) -> bytes:
    if len(block) != 16:
        raise ValueError("Блок должен быть 16 байт")
    state = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i + 4*j]
    Nr = len(round_keys) - 1
    add_round_key(state, round_keys[Nr])
    for round in range(Nr-1, 0, -1):
        inv_shift_rows(state)
        inv_sub_bytes(state)
        add_round_key(state, round_keys[round])
        inv_mix_columns(state)
    inv_shift_rows(state)
    inv_sub_bytes(state)
    add_round_key(state, round_keys[0])
    output = bytearray(16)
    for i in range(4):
        for j in range(4):
            output[i + 4*j] = state[i][j]
    return bytes(output)

def prepare_text(raw_text: str, mode: str = 'text') -> bytes:
    if mode == 'hex':
        hex_str = raw_text.strip().replace(' ', '').replace('0x', '')
        if len(hex_str) % 2 != 0:
            raise ValueError("Hex-строка должна содержать чётное число символов")
        return bytes.fromhex(hex_str)
    else:
        text = raw_text.replace(',', 'зпт').replace('.', 'тчк').replace(' ', '')
        return text.encode('utf-8')

def prepare_key(key_input: str) -> bytes:
    key_hex = key_input.strip().replace(' ', '').replace('0x', '')
    if len(key_hex) not in (32, 48, 64):
        raise ValueError("Ключ должен быть 32, 48 или 64 шестнадцатеричных символа (AES-128, AES-192 или AES-256)")
    return bytes.fromhex(key_hex)

def pad_data(data: bytes) -> bytes:
    padding_len = 16 - (len(data) % 16)
    if padding_len == 16:
        return data
    else:
        return data + b'\x00' * padding_len

def unpad_data(data: bytes) -> bytes:
    return data.rstrip(b'\x00')

def aes_encrypt_data(data: bytes, key: bytes) -> bytes:
    round_keys = key_expansion(key)
    padded_data = pad_data(data)
    encrypted = bytearray()
    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        enc_block = aes_encrypt_block(block, round_keys)
        encrypted.extend(enc_block)
    return bytes(encrypted)

def aes_decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    round_keys = key_expansion(key)
    if len(encrypted_data) % 16 != 0:
        raise ValueError("Длина зашифрованных данных должна быть кратна 16 байтам")
    decrypted = bytearray()
    for i in range(0, len(encrypted_data), 16):
        block = encrypted_data[i:i+16]
        dec_block = aes_decrypt_block(block, round_keys)
        decrypted.extend(dec_block)
    return unpad_data(bytes(decrypted))

def bytes_to_hex_str(data: bytes) -> str:
    return data.hex().upper()

def hex_str_to_bytes(hex_str: str) -> bytes:
    hex_str = hex_str.strip().replace(' ', '').replace('0x', '')
    return bytes.fromhex(hex_str)

=====================================================================
РЕАЛИЗАЦИЯ КУЗНЕЧИК (ГОСТ Р 34.12-2015) — из файла kuznechik (1).py
=====================================================================
PI_KUZ = [
    252,238,221, 17,207,110, 49, 22,251,196,250,218, 35,197,  4, 77,
    233,119,240,219,147, 46,153,186, 23, 54,241,187, 20,205, 95,193,
    249, 24,101, 90,226, 92,239, 33,129, 28, 60, 66,139,  1,142, 79,
    5,132,  2,174,227,106,143,160,  6, 11,237,152,127,212,211, 31,
    235, 52, 44, 81,234,200, 72,171,242, 42,104,162,253, 58,206,204,
    181,112, 14, 86,  8, 12,118, 18,191,114, 19, 71,156,183, 93,135,
    21,161,150, 41, 16,123,154,199,243,145,120,111,157,158,178,177,
    50,117, 25, 61,255, 53,138,126,109, 84,198,128,195,189, 13, 87,
    223,245, 36,169, 62,168, 67,201,215,121,214,246,124, 34,185,  3,
    224, 15,236,222,122,148,176,188,220,232, 40, 80, 78, 51, 10, 74,
    167,151, 96,115, 30,  0, 98, 68, 26,184, 56,130,100,159, 38, 65,
    173, 69, 70,146, 39, 94, 85, 47,140,163,165,125,105,213,149, 59,
    7, 88,179, 64,134,172, 29,247, 48, 55,107,228,136,217,231,137,
    225, 27,131, 73, 76, 63,248,254,141, 83,170,144,202,216,133, 97,
    32,113,103,164, 45, 43,  9, 91,203,155, 37,208,190,229,108, 82,
    89,166,116,210,230,244,180,192,209,102,175,194, 57, 75, 99,182,
]

PI_INV_KUZ = [0] * 256
for i, v in enumerate(PI_KUZ):
    PI_INV_KUZ[v] = i

GF_MOD = 0x1C3

def gf_mul_kuz(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a & 0x100:
            a ^= GF_MOD
        b >>= 1
    return result

L_COEFFS_KUZ = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]

def l_func_kuz(a):
    result = 0
    for i in range(16):
        result ^= gf_mul_kuz(L_COEFFS_KUZ[i], a[i])
    return result

def X_kuz(k, a):
    return [k[i] ^ a[i] for i in range(16)]

def S_kuz(a):
    return [PI_KUZ[b] for b in a]

def S_inv_kuz(a):
    return [PI_INV_KUZ[b] for b in a]

def R_kuz(a):
    new_byte = l_func_kuz(a)
    return [new_byte] + a[:-1]

def R_inv_kuz(a):
    tail = a[1:] + [a[0]]
    new_byte = l_func_kuz(tail)
    return a[1:] + [new_byte]

def L_kuz(a):
    for _ in range(16):
        a = R_kuz(a)
    return a

def L_inv_kuz(a):
    for _ in range(16):
        a = R_inv_kuz(a)
    return a

def _gen_constants():
    consts = []
    for i in range(1, 33):
        consts.append(L_kuz([0] * 15 + [i]))
    return consts

ITER_CONSTS = _gen_constants()

def F_kuz(k, a1, a0):
    lsx = L_kuz(S_kuz(X_kuz(k, a1)))
    return X_kuz(lsx, a0), a1

def key_schedule_kuz(key_bytes):
    k1 = list(key_bytes[:16])
    k2 = list(key_bytes[16:])
    keys = [k1, k2]
    a, b = k1[:], k2[:]
    for i in range(4):
        for j in range(8):
            a, b = F_kuz(ITER_CONSTS[8 * i + j], a, b)
            keys.append(a[:])
            keys.append(b[:])
    return keys

def encrypt_block_kuz(plain_bytes, round_keys):
    a = list(plain_bytes)
    for i in range(9):
        a = L_kuz(S_kuz(X_kuz(round_keys[i], a)))
    return bytes(X_kuz(round_keys[9], a))

def decrypt_block_kuz(cipher_bytes, round_keys):
    a = list(cipher_bytes)
    a = X_kuz(round_keys[9], a)
    for i in range(8, -1, -1):
        a = X_kuz(round_keys[i], S_inv_kuz(L_inv_kuz(a)))
    return bytes(a)

def _pkcs7_pad(data, block=16):
    n = block - len(data) % block
    return data + bytes([n] * n)

def _pkcs7_unpad(data):
    n = data[-1]
    if n < 1 or n > 16:
        raise ValueError("Некорректный padding")
    return data[:-n]

def encrypt_ecb_kuz(data, key_bytes, use_padding=True):
    rk = key_schedule_kuz(key_bytes)
    if use_padding:
        data = _pkcs7_pad(data)
    else:
        if len(data) % 16 != 0:
            raise ValueError("Длина данных должна быть кратна 16 байтам (или используйте use_padding=True)")
    return b''.join(encrypt_block_kuz(data[i:i+16], rk) for i in range(0, len(data), 16))

def decrypt_ecb_kuz(data, key_bytes, use_padding=True):
    if len(data) % 16 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 16 байтам")
    rk = key_schedule_kuz(key_bytes)
    dec = b''.join(decrypt_block_kuz(data[i:i+16], rk) for i in range(0, len(data), 16))
    return _pkcs7_unpad(dec) if use_padding else dec

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
L2N = {c: i+1 for i, c in enumerate(ALPHABET)}
N2L = {i+1: c for i, c in enumerate(ALPHABET)}

def preprocess_ru(text):
    res = []
    for ch in text.lower():
        if ch == ' ':
            continue
        elif ch == ',':
            res.append('зпт')
        elif ch == '.':
            res.append('тчк')
        elif ch in ALPHABET:
            res.append(ch)
    return ''.join(res)

def postprocess_ru(text):
    return text.replace('зпт', ',').replace('тчк', '.')

def text_to_bytes_ru(text):
    return bytes([L2N[c] for c in text])

def bytes_to_text_ru(data):
    result = []
    for b in data:
        if 1 <= b <= 32:
            result.append(N2L[b])
    return ''.join(result)

def encrypt_russian(plain, key_hex):
    processed = preprocess_ru(plain)
    if not processed:
        raise ValueError("Текст пуст после предобработки")
    data = text_to_bytes_ru(processed)
    key = bytes.fromhex(key_hex)
    enc = encrypt_ecb_kuz(data, key, use_padding=True)
    return enc.hex().upper()

def decrypt_russian(cipher_hex, key_hex):
    key = bytes.fromhex(key_hex)
    enc = bytes.fromhex(cipher_hex)
    dec = decrypt_ecb_kuz(enc, key, use_padding=True)
    return bytes_to_text_ru(dec)

def run_gost_test():
    KEY = bytes.fromhex("8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef")
    PLAIN = bytes.fromhex("1122334455667700ffeeddccbbaa9988")
    EXPECTED = "7f679d90bebc24305a468d42b9d4edcd"
    EXP_KEYS = [
        "8899aabbccddeeff0011223344556677",
        "fedcba98765432100123456789abcdef",
        "db31485315694343228d2b3bef05d129",
        "57646468c44a5e28d3e59246f429f1ac",
        "bd079435165c6432b532e82834da581b",
        "51e640757e8745de705727265a0098b1",
        "5a7925017b9fdd3ed72a91a22286f984",
        "bb44e25378c73123a5f32f73cdb6e517",
        "72e9dd7416bcf45b755dbaa88e4a4043",
    ]
    rk = key_schedule_kuz(KEY)
    print("── Раундовые ключи K1..K9 (сравнение с ГОСТ А.1.4) ──")
    for i in range(9):
        kh = bytes(rk[i]).hex()
        exp = EXP_KEYS[i]
        ok = '✅' if kh == exp else '❌'
        print(f"  K{i+1:2d}: {kh}  {ok}")
    print(f"  K10: {bytes(rk[9]).hex()}")
    print("── Промежуточные шаги (А.1.5) ──")
    EXP_STEPS = [
        ("X[K1](a)", "99bb99ff99bb99ffffffffffffffffff"),
        ("S(X[K1](a))", "e87de8b6e87de8b6b6b6b6b6b6b6b6b6"),
        ("LSX[K1](a)", "e297b686e355b0a1cf4a2f9249140830"),
    ]
    a = list(PLAIN)
    xk = X_kuz(rk[0], a)
    sx = S_kuz(xk)
    lsx = L_kuz(sx)
    steps = [bytes(xk).hex(), bytes(sx).hex(), bytes(lsx).hex()]
    for (name, exp), got in zip(EXP_STEPS, steps):
        ok = '✅' if got == exp else '❌'
        print(f"  {name:<18}: {got}  {ok}")
    enc = encrypt_block_kuz(PLAIN, rk)
    dec = decrypt_block_kuz(enc, rk)
    print(f"── Шифрование блока ──")
    print(f"  Открытый : {PLAIN.hex()}")
    print(f"  Ожидается: {EXPECTED}")
    print(f"  Получено : {enc.hex()}")
    print(f"  Результат: {'✅ ВЕРНО' if enc.hex() == EXPECTED else '❌ ОШИБКА'}")
    print(f"── Расшифрование блока ──")
    print(f"  Шифртекст: {enc.hex()}")
    print(f"  Получено : {dec.hex()}")
    print(f"  Результат: {'✅ ВЕРНО' if dec == PLAIN else '❌ ОШИБКА'}")
    print(f"── Тест на тексте >1000 байт ──")
    long_text = b"Kuznyechik GOST R 34.12-2015 block cipher test data. " * 20
    enc2 = encrypt_ecb_kuz(long_text, KEY, use_padding=True)
    dec2 = decrypt_ecb_kuz(enc2, KEY, use_padding=True)
    ok2 = dec2 == long_text
    print(f"  Длина       : {len(long_text)} байт")
    print(f"  Зашифровано : {len(enc2)} байт")
    print(f"  Расшифровано: {'✅ Совпадает' if ok2 else '❌ Не совпадает'}")
    print(f"  Шифртекст   : {enc2.hex()[:64]}...")

=====================================================================
ГЛАВНОЕ МЕНЮ (интегрированное)
=====================================================================
def input_hex(prompt, length=None):
    while True:
        try:
            val = bytes.fromhex(input(prompt).replace(" ", ""))
            if length and len(val) != length:
                raise ValueError
            return val
        except ValueError:
            print(f"Ошибка: ожидается HEX ({length} байт если указано)")

def get_key(prompt="Ключ (64 hex, Enter=тестовый): "):
    kh = input(prompt).strip().replace(' ', '')
    if not kh:
        kh = "8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef"
        print(f"  Используется тестовый ключ: {kh}")
    if len(kh) != 64 or not all(c in '0123456789abcdefABCDEF' for c in kh):
        raise ValueError("Ключ должен содержать ровно 64 hex-символа")
    return kh

def main():
    while True:
        print("\n" + "= "*60)
        print("БЛОК G: МАГМА, AES (FIPS-197), КУЗНЕЧИК (ГОСТ Р 34.12-2015)")
        print("= "*60)
        print("[1] МАГМА")
        print("[2] AES (полная реализация)")
        print("[3] КУЗНЕЧИК (полная реализация)")
        print("[0] Выход")
        choice = input("\nВыбор: ").strip()
        
        if choice == "0":
            print("До свидания!")
            sys.exit(0)
        
        elif choice == "1":
            print("\n--- МАГМА ---")
            k = input_hex("  Ключ (32 байта HEX): ", 32)
            d = input_hex("  Данные (8 байт HEX): ", 8)
            mode = input("  1 - Шифр, 2 - Расшифр: ").strip()
            try:
                result = magma_process(d, k, mode == '1')
                print(f"  Результат: {result.hex().upper()}")
            except Exception as e:
                print(f"  Ошибка: {e}")
        
        elif choice == "2":
            print("\n--- AES ---")
            print("Подменю:")
            print("  1. Шифрование текста (русский/латиница, замена , . → зпт/тчк)")
            print("  2. Расшифрование текста")
            print("  3. Шифрование hex-данных")
            print("  4. Расшифрование hex-данных")
            sub = input("Выбор: ").strip()
            
            if sub == "1":
                plaintext = input("Введите открытый текст: ").strip()
                key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
                try:
                    key = prepare_key(key_hex)
                    data_bytes = prepare_text(plaintext, mode='text')
                    print(f"Подготовленные данные (hex): {bytes_to_hex_str(data_bytes)}")
                    encrypted_data = aes_encrypt_data(data_bytes, key)
                    print("\nЗашифрованный текст (hex):")
                    print(bytes_to_hex_str(encrypted_data))
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif sub == "2":
                cipher_hex = input("Введите шифртекст (hex): ").strip()
                key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
                try:
                    key = prepare_key(key_hex)
                    cipher_bytes = hex_str_to_bytes(cipher_hex)
                    decrypted_data = aes_decrypt_data(cipher_bytes, key)
                    try:
                        plaintext = decrypted_data.decode('utf-8')
                        plaintext = plaintext.replace('зпт', ',').replace('тчк', '.')
                        print("\nРасшифрованный текст:")
                        print(plaintext)
                    except UnicodeDecodeError:
                        print("\nРасшифрованные данные (hex):")
                        print(decrypted_data.hex().upper())
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif sub == "3":
                plain_hex = input("Введите открытые данные в hex: ").strip()
                key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
                try:
                    key = prepare_key(key_hex)
                    data_bytes = prepare_text(plain_hex, mode='hex')
                    encrypted_data = aes_encrypt_data(data_bytes, key)
                    print("\nЗашифрованный текст (hex):")
                    print(bytes_to_hex_str(encrypted_data))
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif sub == "4":
                cipher_hex = input("Введите шифртекст (hex): ").strip()
                key_hex = input("Введите ключ (32/48/64 hex-символа): ").strip()
                try:
                    key = prepare_key(key_hex)
                    cipher_bytes = hex_str_to_bytes(cipher_hex)
                    decrypted_data = aes_decrypt_data(cipher_bytes, key)
                    print("\nРасшифрованные данные (hex):")
                    print(decrypted_data.hex().upper())
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            else:
                print("Неверный выбор.")
        
        elif choice == "3":
            print("\n--- КУЗНЕЧИК ---")
            print("Подменю:")
            print("  1. Шифрование русского текста")
            print("  2. Расшифрование русского текста")
            print("  3. Шифрование hex-данных")
            print("  4. Расшифрование hex-данных")
            print("  5. Тест по ГОСТ Р 34.12-2015 (А.1)")
            sub = input("Выбор: ").strip()
            
            if sub == "1":
                try:
                    kh = get_key()
                    txt = input("Текст (русские буквы): ").strip()
                    enc = encrypt_russian(txt, kh)
                    print(f"Шифртекст (hex): {enc}")
                    save = input("Сохранить в файл? (y/n): ").strip().lower()
                    if save == 'y':
                        fn = input("Имя файла (kuz_cipher.bin): ").strip() or "kuz_cipher.bin"
                        open(fn, 'wb').write(bytes.fromhex(enc))
                        print(f"✅ Сохранено в '{fn}'")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
            
            elif sub == "2":
                try:
                    kh = get_key()
                    chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                    dec = decrypt_russian(chex, kh)
                    print(f"Расшифрованный текст: {dec}")
                    r = input("Восстановить знаки препинания? (y/n): ").strip().lower()
                    if r == 'y':
                        print(f"С пунктуацией: {postprocess_ru(dec)}")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
            
            elif sub == "3":
                try:
                    kh = get_key()
                    phex = input("Открытый текст (hex): ").strip().replace(' ', '')
                    pb = bytes.fromhex(phex)
                    if len(pb) % 16 == 0:
                        enc = encrypt_ecb_kuz(pb, bytes.fromhex(kh), use_padding=False)
                    else:
                        print("  Длина не кратна 16 — будет применён PKCS#7 padding")
                        enc = encrypt_ecb_kuz(pb, bytes.fromhex(kh), use_padding=True)
                    print(f"Шифртекст (hex): {enc.hex().upper()}")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
            
            elif sub == "4":
                try:
                    kh = get_key()
                    chex = input("Шифртекст (hex): ").strip().replace(' ', '')
                    cb = bytes.fromhex(chex)
                    p = input("При шифровании использовался padding? (y/n): ").strip().lower()
                    use_p = (p == 'y')
                    dec = decrypt_ecb_kuz(cb, bytes.fromhex(kh), use_padding=use_p)
                    print(f"Открытый текст (hex): {dec.hex().upper()}")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
            
            elif sub == "5":
                run_gost_test()
            
            else:
                print("Неверный выбор.")
        
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()