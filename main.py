from my_dataclasses import Code, ReturnData
from typing import List, Tuple


def count_quantity(text: str) -> List[Tuple[str, int]]:
    '''
    Считаем количество вхождений каждого символа и сортируем по убыванию
    '''
    frequency = {}
    for i in text:
        frequency[i] = frequency.get(i, 0) + 1

    return sorted(frequency.items(), key=lambda x: x[1], reverse=True)


def get_median(freqs: List[Tuple[str, int]], start: int, end: int) -> int:
    '''
    Ищем точку от start до end, в которой сумма частот слева и справа +- равна
    '''
    if end - start <= 1:
        return start

    sum_left = sum(i for _, i in freqs)
    sum_right = freqs[end - 1][1]
    m = end - 1
    best_diff = abs(sum_left - sum_right)

    while m > start:
        m -= 1
        if m < start:
            break
        sum_left -= freqs[m][1]
        sum_right += freqs[m][1]
        current_diff = abs(sum_left - sum_right)
        if current_diff < best_diff:
            best_diff = current_diff
        else:
            break
    return m


def encode(text: str, need_to_print=False) -> ReturnData:
    '''
    Кодируем текст с помощью кода Фано
    '''
    frequencies = count_quantity(text)
    codes = [[i[0], ''] for i in frequencies]

    def make_fano_code(start: int, end: int, current_code: str) -> None:
        '''
        Делаем разделение по медиане и запускаем рекрсивно опять
        (по сути строим дерево, где левое ответвление - 0, а правое - 1)
        '''
        if end <= start:
            return

        if end - start == 1:
            codes[start][1] = current_code
            return

        m = get_median(frequencies, start, end)

        for i in range(start, end):
            if i <= m:
                codes[i][1] = current_code + '0'
            else:
                codes[i][1] = current_code + '1'

        make_fano_code(start, m + 1, current_code + '0')
        make_fano_code(m + 1, end, current_code + '1')

    make_fano_code(0, len(frequencies), '')
    codes_dict = {char: code for char, code in codes}

    if need_to_print:
        print('Получившийся список из кодов:')
        for i in codes_dict:
            print(f"{'Символ пробела' if i == ' ' else i} - {codes_dict[i]}")

    encoded_text = ''
    for i in text:
        encoded_text += codes_dict[i]  # Происходит кодирование

    code_objects = [Code(char, code) for char, code in codes]

    return ReturnData(encoded_text, code_objects)


def decode(data: ReturnData, need_to_print=False) -> str:
    '''
    Просто ищем подходящий нам код, так как прямой Фано, то идём в прямом
    порядке по закодированному тексту
    '''
    codes_dict = {code_obj.code: code_obj.letter for code_obj in data.codes}

    decoded_text = ""
    current_code = ""

    for i in data.encoded_text:
        current_code += i
        if current_code in codes_dict.keys():
            found_char = codes_dict[current_code]
            decoded_text += found_char
            current_code = ""
            if need_to_print:
                print(f"""
                      Найден код: {current_code},
                      ему соответствует {
                          'Символ пробела' if found_char == ' ' else found_char
                        }
                """)
                print(f"Текст на данный момент: {decoded_text}")
    return decoded_text


def main():
    text_type = 'small_text.txt'
    with open(text_type, 'rb') as file:  # Открываем в бинарном режиме
        data = file.read()
        original_bits = len(data) * 8  # Реальный размер в битах
        text = data.decode('utf-8')    # Декодируем в строку для обработки

    encoded_data = encode(text, True)
    encoded_text = encoded_data.encoded_text
    print('Маленький текст')
    print(f"Вес исходного текста: {original_bits} бит")
    print(f"Вес закодированного текста: {len(encoded_text)} бит")

    text_type = 'large_text.txt'
    with open(text_type, 'rb') as file:  # Открываем в бинарном режиме
        data = file.read()
        original_bits = len(data) * 8
        text = data.decode('utf-8', errors='ignore')

    encoded_data = encode(text, False)
    encoded_text = encoded_data.encoded_text
    print('Большой текст')
    print(f"Вес исходного текста: {original_bits} бит")
    print(f"Вес закодированного текста: {len(encoded_text)} бит")


if __name__ == "__main__":
    main()
