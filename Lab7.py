import sys
import struct

# =====================================================================
# МАГМА — ГОСТ Р 34.12-2015 (из magma 2.py)
# =====================================================================
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

def magma_t(a):
    result = 0
    for i in range(8):
        nibble = (a >> (4*i)) & 0xF
        result |= PI_MAGMA[i][nibble] << (4*i)
    return result

def magma_rot11(x):
    return ((x << 11) | (x >> 21)) & 0xFFFFFFFF

def magma_g(k, a):
    return magma_rot11(magma_t((a + k) & 0xFFFFFFFF))

def magma_key_schedule(key_bytes):
    k = [int.from_bytes(key_bytes[4*i:4*i+4], 'big') for i in range(8)]
    return k * 3 + k[::-1]

def magma_encrypt_block(blk, rk):
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    for i in range(31):
        a1, a0 = a0, a1 ^ magma_g(rk[i], a0)
    a1 = a1 ^ magma_g(rk[31], a0)
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def magma_decrypt_block(blk, rk):
    a1 = int.from_bytes(blk[:4], 'big')
    a0 = int.from_bytes(blk[4:], 'big')
    a1 = a1 ^ magma_g(rk[31], a0)
    for i in range(30, -1, -1):
        a1, a0 = a0 ^ magma_g(rk[i], a1), a1
    return a1.to_bytes(4, 'big') + a0.to_bytes(4, 'big')

def magma_pad(data):
    n = 8 - len(data) % 8
    return data + bytes([n]*n)

def magma_unpad(data):
    return data[:-data[-1]]

def magma_encrypt_ecb(data, key_bytes, use_padding=True):
    rk = magma_key_schedule(key_bytes)
    if use_padding:
        data = magma_pad(data)
    else:
        if len(data) % 8 != 0:
            raise ValueError("Длина данных должна быть кратна 8 байтам при use_padding=False")
    return b''.join(magma_encrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))

def magma_decrypt_ecb(data, key_bytes, use_padding=True):
    rk = magma_key_schedule(key_bytes)
    if len(data) % 8 != 0:
        raise ValueError("Длина шифртекста должна быть кратна 8")
    dec = b''.join(magma_decrypt_block(data[i:i+8], rk) for i in range(0, len(data), 8))
    if use_padding:
        return magma_unpad(dec)
    else:
        return dec

# =====================================================================
# AES (FIPS-197) (из aes.py)
# =====================================================================
SBOX_AES = [
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

INV_SBOX_AES = [
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

Rcon_AES = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a]

def aes_sub_byte(b):
    return SBOX_AES[b >> 4][b & 0x0F]

def aes_inv_sub_byte(b):
    return INV_SBOX_AES[b >> 4][b & 0x0F]

def aes_sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = aes_sub_byte(state[i][j])

def aes_inv_sub_bytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = aes_inv_sub_byte(state[i][j])

def aes_shift_rows(state):
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][1], state[1][2], state[1][3], state[1][0]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][3], state[3][0], state[3][1], state[3][2]

def aes_inv_shift_rows(state):
    state[1][0], state[1][1], state[1][2], state[1][3] = state[1][3], state[1][0], state[1][1], state[1][2]
    state[2][0], state[2][1], state[2][2], state[2][3] = state[2][2], state[2][3], state[2][0], state[2][1]
    state[3][0], state[3][1], state[3][2], state[3][3] = state[3][1], state[3][2], state[3][3], state[3][0]

def aes_xtime(b):
    if b & 0x80: return ((b << 1) & 0xFF) ^ 0x1B
    else: return (b << 1) & 0xFF

def aes_mul(a, b):
    result = 0
    while b:
        if b & 1: result ^= a
        a = aes_xtime(a)
        b >>= 1
    return result

def aes_mix_columns(state):
    for c in range(4):
        s0, s1, s2, s3 = state[0][c], state[1][c], state[2][c], state[3][c]
        state[0][c] = aes_xtime(s0) ^ (aes_xtime(s1) ^ s1) ^ s2 ^ s3
        state[1][c] = s0 ^ aes_xtime(s1) ^ (aes_xtime(s2) ^ s2) ^ s3
        state[2][c] = s0 ^ s1 ^ aes_xtime(s2) ^ (aes_xtime(s3) ^ s3)
        state[3][c] = (aes_xtime(s0) ^ s0) ^ s1 ^ s2 ^ aes_xtime(s3)

def aes_inv_mix_columns(state):
    for c in range(4):
        s0, s1, s2, s3 = state[0][c], state[1][c], state[2][c], state[3][c]
        state[0][c] = aes_mul(0x0e, s0) ^ aes_mul(0x0b, s1) ^ aes_mul(0x0d, s2) ^ aes_mul(0x09, s3)
        state[1][c] = aes_mul(0x09, s0) ^ aes_mul(0x0e, s1) ^ aes_mul(0x0b, s2) ^ aes_mul(0x0d, s3)
        state[2][c] = aes_mul(0x0d, s0) ^ aes_mul(0x09, s1) ^ aes_mul(0x0e, s2) ^ aes_mul(0x0b, s3)
        state[3][c] = aes_mul(0x0b, s0) ^ aes_mul(0x0d, s1) ^ aes_mul(0x09, s2) ^ aes_mul(0x0e, s3)

def aes_add_round_key(state, round_key):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= round_key[i][j]

def aes_key_expansion(key):
    Nk = len(key) // 4
    Nr = Nk + 6
    w = []
    for i in range(Nk):
        w.append(int.from_bytes(key[i*4:(i+1)*4], 'big'))
    for i in range(Nk, 4*(Nr+1)):
        temp = w[i-1]
        if i % Nk == 0:
            temp = ((temp << 8) & 0xFFFFFFFF) | (temp >> 24)
            temp = (aes_sub_byte((temp >> 24) & 0xFF) << 24) | \
                   (aes_sub_byte((temp >> 16) & 0xFF) << 16) | \
                   (aes_sub_byte((temp >> 8) & 0xFF) << 8) | \
                   aes_sub_byte(temp & 0xFF)
            temp ^= (Rcon_AES[i//Nk - 1] << 24)
        elif Nk > 6 and i % Nk == 4:
            temp = (aes_sub_byte((temp >> 24) & 0xFF) << 24) | \
                   (aes_sub_byte((temp >> 16) & 0xFF) << 16) | \
                   (aes_sub_byte((temp >> 8) & 0xFF) << 8) | \
                   aes_sub_byte(temp & 0xFF)
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
    state = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i + 4*j]
    Nr = len(round_keys) - 1
    aes_add_round_key(state, round_keys[0])
    for round in range(1, Nr):
        aes_sub_bytes(state)
        aes_shift_rows(state)
        aes_mix_columns(state)
        aes_add_round_key(state, round_keys[round])
    aes_sub_bytes(state)
    aes_shift_rows(state)
    aes_add_round_key(state, round_keys[Nr])
    output = bytearray(16)
    for i in range(4):
        for j in range(4):
            output[i + 4*j] = state[i][j]
    return bytes(output)

def aes_decrypt_block(block: bytes, round_keys: list) -> bytes:
    state = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i + 4*j]
    Nr = len(round_keys) - 1
    aes_add_round_key(state, round_keys[Nr])
    for round in range(Nr-1, 0, -1):
        aes_inv_shift_rows(state)
        aes_inv_sub_bytes(state)
        aes_add_round_key(state, round_keys[round])
        aes_inv_mix_columns(state)
    aes_inv_shift_rows(state)
    aes_inv_sub_bytes(state)
    aes_add_round_key(state, round_keys[0])
    output = bytearray(16)
    for i in range(4):
        for j in range(4):
            output[i + 4*j] = state[i][j]
    return bytes(output)

def aes_pad_data(data: bytes) -> bytes:
    padding_len = 16 - (len(data) % 16)
    if padding_len == 16: return data
    return data + b'\x00' * padding_len

def aes_unpad_data(data: bytes) -> bytes:
    return data.rstrip(b'\x00')

def aes_encrypt_data(data: bytes, key: bytes) -> bytes:
    round_keys = aes_key_expansion(key)
    padded_data = aes_pad_data(data)
    encrypted = bytearray()
    for i in range(0, len(padded_data), 16):
        block = padded_data[i:i+16]
        encrypted.extend(aes_encrypt_block(block, round_keys))
    return bytes(encrypted)

def aes_decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    round_keys = aes_key_expansion(key)
    if len(encrypted_data) % 16 != 0: raise ValueError("Длина зашифрованных данных должна быть кратна 16 байтам")
    decrypted = bytearray()
    for i in range(0, len(encrypted_data), 16):
        block = encrypted_data[i:i+16]
        decrypted.extend(aes_decrypt_block(block, round_keys))
    return aes_unpad_data(bytes(decrypted))

# =====================================================================
# КУЗНЕЧИК — ГОСТ Р 34.12-2015 (из kuznechik.py)
# =====================================================================
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
for i, v in enumerate(PI_KUZ): PI_INV_KUZ[v] = i

GF_MOD_KUZ = 0x1C3
L_COEFFS_KUZ = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]

def kuz_gf_mul(a, b):
    result = 0
    while b:
        if b & 1: result ^= a
        a <<= 1
        if a & 0x100: a ^= GF_MOD_KUZ
        b >>= 1
    return result

def kuz_l_func(a):
    result = 0
    for i in range(16): result ^= kuz_gf_mul(L_COEFFS_KUZ[i], a[i])
    return result

def kuz_X(k, a): return [k[i] ^ a[i] for i in range(16)]
def kuz_S(a): return [PI_KUZ[b] for b in a]
def kuz_S_inv(a): return [PI_INV_KUZ[b] for b in a]

def kuz_R(a):
    new_byte = kuz_l_func(a)
    return [new_byte] + a[:-1]

def kuz_R_inv(a):
    tail = a[1:] + [a[0]]
    new_byte = kuz_l_func(tail)
    return a[1:] + [new_byte]

def kuz_L(a):
    for _ in range(16): a = kuz_R(a)
    return a

def kuz_L_inv(a):
    for _ in range(16): a = kuz_R_inv(a)
    return a

def _gen_kuz_constants():
    consts = []
    for i in range(1, 33): consts.append(kuz_L([0] * 15 + [i]))
    return consts

ITER_CONSTS_KUZ = _gen_kuz_constants()

def kuz_F(k, a1, a0):
    lsx = kuz_L(kuz_S(kuz_X(k, a1)))
    return kuz_X(lsx, a0), a1

def kuz_key_schedule(key_bytes):
    k1, k2 = list(key_bytes[:16]), list(key_bytes[16:])
    keys = [k1, k2]
    a, b = k1[:], k2[:]
    for i in range(4):
        for j in range(8):
            a, b = kuz_F(ITER_CONSTS_KUZ[8 * i + j], a, b)
        keys.append(a[:])
        keys.append(b[:])
    return keys

def kuz_encrypt_block(plain_bytes, round_keys):
    a = list(plain_bytes)
    for i in range(9):
        a = kuz_L(kuz_S(kuz_X(round_keys[i], a)))
    return bytes(kuz_X(round_keys[9], a))

def kuz_decrypt_block(cipher_bytes, round_keys):
    a = list(cipher_bytes)
    a = kuz_X(round_keys[9], a)
    for i in range(8, -1, -1):
        a = kuz_X(round_keys[i], kuz_S_inv(kuz_L_inv(a)))
    return bytes(a)

def kuz_pkcs7_pad(data, block=16):
    n = block - len(data) % block
    return data + bytes([n] * n)

def kuz_pkcs7_unpad(data):
    n = data[-1]
    if n < 1 or n > 16: raise ValueError("Некорректный padding")
    return data[:-n]

def kuz_encrypt_ecb(data, key_bytes, use_padding=True):
    rk = kuz_key_schedule(key_bytes)
    if use_padding: data = kuz_pkcs7_pad(data)
    else:
        if len(data) % 16 != 0: raise ValueError("Длина данных должна быть кратна 16 байтам (или используйте use_padding=True)")
    return b''.join(kuz_encrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))

def kuz_decrypt_ecb(data, key_bytes, use_padding=True):
    if len(data) % 16 != 0: raise ValueError("Длина шифртекста должна быть кратна 16 байтам")
    rk = kuz_key_schedule(key_bytes)
    dec = b''.join(kuz_decrypt_block(data[i:i+16], rk) for i in range(0, len(data), 16))
    return kuz_pkcs7_unpad(dec) if use_padding else dec

ALPHABET_RU = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
L2N_RU = {c: i+1 for i, c in enumerate(ALPHABET_RU)}
N2L_RU = {i+1: c for i, c in enumerate(ALPHABET_RU)}

def kuz_preprocess_ru(text):
    res = []
    for ch in text.lower():
        if ch == ' ': continue
        elif ch == ',': res.append('зпт')
        elif ch == '.': res.append('тчк')
        elif ch in ALPHABET_RU: res.append(ch)
    return ''.join(res)

def kuz_postprocess_ru(text):
    return text.replace('зпт', ',').replace('тчк', '.')

def kuz_text_to_bytes_ru(text):
    return bytes([L2N_RU[c] for c in text])

def kuz_bytes_to_text_ru(data):
    result = []
    for b in data:
        if 1 <= b <= 32: result.append(N2L_RU[b])
    return ''.join(result)

def kuz_encrypt_russian(plain, key_hex):
    processed = kuz_preprocess_ru(plain)
    if not processed: raise ValueError("Текст пуст после предобработки")
    data = kuz_text_to_bytes_ru(processed)
    key  = bytes.fromhex(key_hex)
    enc  = kuz_encrypt_ecb(data, key, use_padding=True)
    return enc.hex().upper()

def kuz_decrypt_russian(cipher_hex, key_hex):
    key = bytes.fromhex(key_hex)
    enc = bytes.fromhex(cipher_hex)
    dec = kuz_decrypt_ecb(enc, key, use_padding=True)
    return kuz_bytes_to_text_ru(dec)

# =====================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ГЛАВНОЕ МЕНЮ
# =====================================================================
def prepare_text(raw_text: str, mode: str = 'text') -> bytes:
    if mode == 'hex':
        hex_str = "".join(raw_text.split()).replace('0x', '')
        if len(hex_str) % 2 != 0: raise ValueError("Hex-строка должна содержать чётное число символов")
        return bytes.fromhex(hex_str)
    else:
        text = raw_text.replace(',', 'зпт').replace('.', 'тчк').replace(' ', '')
        return text.encode('utf-8')

def prepare_key(key_input: str, expected_lengths) -> bytes:
    key_hex = "".join(key_input.split()).replace('0x', '')
    if len(key_hex) not in expected_lengths:
        raise ValueError(f"Ключ должен быть одной из следующих длин в hex-символах: {expected_lengths}")
    return bytes.fromhex(key_hex)

def hex_str_to_bytes(hex_str: str) -> bytes:
    hex_str = "".join(hex_str.split()).replace('0x', '')
    return bytes.fromhex(hex_str)

def get_key(prompt, default_key, lengths):
    kh = "".join(input(prompt).split()).replace('0x', '')
    if not kh:
        kh = default_key
        print(f"  Используется тестовый ключ: {kh}")
    if len(kh) not in lengths or not all(c in '0123456789abcdefABCDEF' for c in kh):
        raise ValueError(f"Ключ должен содержать {lengths} hex-символов")
    return kh

def main():
    while True:
        print("\n" + "="*50)
        print("БЛОК G: КОМБИНАЦИОННЫЕ ШИФРЫ")
        print("\n" + "="*50)
        print("[1] МАГМА    (ГОСТ Р 34.12-2015)")
        print("[2] AES      (FIPS-197)")
        print("[3] КУЗНЕЧИК (ГОСТ Р 34.12-2015)")
        print("[0] Выход")
        choice = input("\nВыбор: ").strip()
        
        if choice == "0":
            print("До свидания!")
            sys.exit(0)
        
        elif choice == "1":
            print("\n--- МАГМА ---")
            print("  1. Зашифровать hex-данные")
            print("  2. Расшифровать hex-данные")
            sub = input("Выбор: ").strip()
            if sub in ('1', '2'):
                try:
                    kh = get_key("Ключ (64 hex, Enter=тестовый): ", 
                                 "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff", [64])
                    data_hex = "".join(input("Данные (HEX): ").split()).replace('0x', '')
                    data_bytes = bytes.fromhex(data_hex)
                    key = bytes.fromhex(kh)
                    use_p = (len(data_bytes) % 8 != 0)
                    
                    if sub == '1':
                        res = magma_encrypt_ecb(data_bytes, key, use_padding=use_p)
                        print(f"\nШифртекст (hex): \n{res.hex().upper()}")
                    else:
                        res = magma_decrypt_ecb(data_bytes, key, use_padding=False)
                        print(f"\nОткрытый текст (hex): \n{res.hex().upper()}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            else:
                print("Неверный выбор.")
        
        elif choice == "2":
            print("\n--- AES ---")
            print("  1. Шифрование текста (utf-8)")
            print("  2. Расшифрование текста")
            print("  3. Шифрование hex-данных")
            print("  4. Расшифрование hex-данных")
            sub = input("Выбор: ").strip()
            
            if sub in ('1', '2', '3', '4'):
                try:
                    is_text_mode = sub in ('1', '2')
                    is_encrypt = sub in ('1', '3')
                    
                    data_input = input(f"Введите {'текст' if is_text_mode and is_encrypt else 'hex-данные'}: ")
                    kh = get_key("Введите ключ (32/48/64 hex-символа, Enter=тест 128): ", 
                                 "000102030405060708090a0b0c0d0e0f", [32, 48, 64])
                    key = bytes.fromhex(kh)
                    
                    if is_encrypt:
                        data_bytes = prepare_text(data_input, 'text' if is_text_mode else 'hex')
                        encrypted = aes_encrypt_data(data_bytes, key)
                        print(f"\nЗашифрованный текст (hex): \n{encrypted.hex().upper()}")
                    else:
                        cipher_bytes = hex_str_to_bytes(data_input)
                        decrypted = aes_decrypt_data(cipher_bytes, key)
                        if is_text_mode:
                            try:
                                plaintext = decrypted.decode('utf-8').replace('зпт', ',').replace('тчк', '.')
                                print(f"\nРасшифрованный текст: \n{plaintext}")
                            except UnicodeDecodeError:
                                print(f"\nНе удалось декодировать текст. Данные (hex): \n{decrypted.hex().upper()}")
                        else:
                            print(f"\nРасшифрованные данные (hex): \n{decrypted.hex().upper()}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            else:
                print("Неверный выбор.")
        
        elif choice == "3":
            print("\n--- КУЗНЕЧИК ---")
            print("  1. Шифрование русского текста")
            print("  2. Расшифрование русского текста")
            print("  3. Шифрование hex-данных")
            print("  4. Расшифрование hex-данных")
            sub = input("Выбор: ").strip()
            
            if sub in ('1', '2', '3', '4'):
                try:
                    kh = get_key("Ключ (64 hex, Enter=тестовый): ", 
                                 "8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef", [64])
                    
                    if sub == '1':
                        txt = input("Текст (русские буквы): ").strip()
                        enc = kuz_encrypt_russian(txt, kh)
                        print(f"\nШифртекст (hex): \n{enc}")
                    elif sub == '2':
                        chex = "".join(input("Шифртекст (hex): ").split())
                        dec = kuz_decrypt_russian(chex, kh)
                        print(f"\nРасшифрованный текст: \n{kuz_postprocess_ru(dec)}")
                    elif sub == '3':
                        phex = "".join(input("Открытый текст (hex): ").split())
                        pb = bytes.fromhex(phex)
                        use_p = (len(pb) % 16 != 0)
                        if use_p: print("  Длина не кратна 16 — будет применён PKCS#7 padding")
                        enc = kuz_encrypt_ecb(pb, bytes.fromhex(kh), use_padding=use_p)
                        print(f"\nШифртекст (hex): \n{enc.hex().upper()}")
                    elif sub == '4':
                        chex = "".join(input("Шифртекст (hex): ").split())
                        cb = bytes.fromhex(chex)
                        p = input("При шифровании использовался padding? (y/n, Enter = нет): ").strip().lower()
                        use_p = (p == 'y')
                        dec = kuz_decrypt_ecb(cb, bytes.fromhex(kh), use_padding=use_p)
                        print(f"\nОткрытый текст (hex): \n{dec.hex().upper()}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            else:
                print("Неверный выбор.")
        
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()