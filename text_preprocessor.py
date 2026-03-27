def convert_to_e(text): #преобразование е в ё
    return text.replace('ё', 'е').replace('Ё', 'Е')


def to_lowercase(text): #преобразование в строчные буквы
    return text.lower()


def remove_spaces(text): #удаление пробелов
    return text.replace(' ', '')


def preprocess_text(text, convert_yo=True, to_lower=True, remove_spaces_flag=True): #общая функция
    result = text
    
    if convert_yo:
        result = convert_to_e(result)
    
    if to_lower:
        result = to_lowercase(result)
    
    if remove_spaces_flag:
        result = remove_spaces(result)
    
    return result