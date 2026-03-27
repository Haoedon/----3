def convert_punctuation(text, to_word=True):
    punct_dict = {
        ' ': 'прб',
        '.': 'тчк',
        ',': 'зпт',
        '?': 'впр',
        '!': 'вск',
        ':': 'двтч',
        ';': 'тчзпт',
        '-': 'тире',
        '(': 'скоб',
        ')': 'скобз',
        '"': 'квч',
        "'": 'апстр'
    }

    result = text

    if to_word:
        for punct, word in punct_dict.items():
            result = result.replace(punct, f" {word} ")
    else:
        for punct, word in punct_dict.items():
            result = result.replace(f" {word} ", punct)

    result = ' '.join(result.split())
    return result