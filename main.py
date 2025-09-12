from my_dataclasses import Code, ReturnData
from typing import List, Tuple

def count_quantity(text: str) -> List[Tuple[str, int]]: #Считаем количество вхождений каждого символа и сортируем по убыванию
    frequency = {} 
    for i in text:
        frequency[i] = frequency.get(i, 0) + 1

    sorted_frequency = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_frequency

def get_median(frequencies: List[Tuple[str, int]], start: int, end: int) -> int: #Ищем точку от start до end, в которой сумма частот слева и справа +- равна
    
    if end - start <= 1:
        return start

    sum_left = sum(i for _, i in frequencies)
    sum_right = frequencies[end - 1][1]
    m = end - 1
    best_diff = abs(sum_left - sum_right)
    best_m = m
    
    while m > start:
        m -= 1
        if m < start: 
            break
            
        sum_left -= frequencies[m][1]
        sum_right += frequencies[m][1]
        
        current_diff = abs(sum_left - sum_right)
        
        if current_diff < best_diff:
            best_diff = current_diff
            best_m = m
        else:
            break
    return best_m



def encode(text: str, need_to_print = False) -> ReturnData:#Кодируем
    frequencies = count_quantity(text)
    codes = [[i[0], ''] for i in frequencies]
    def make_fano_code(start: int, end: int, current_code: str) -> None: #Делаем разделение по медиане и запускаем рекрсивно опять (по сути строим дерево, где левое ответвление - 0, а правое - 1)
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
    codes_dict = {char : code for char, code in codes}

    if need_to_print:
        print('Получившийся список из кодов:')
        for i in codes_dict:
            print(f'{'Символ пробела' if i == ' ' else i} - {codes_dict[i]}')

    encoded_text = ''
    for i in text:
        encoded_text += codes_dict[i] #Происходит кодирование

    code_objects = [Code(char, code) for char, code in codes]

    return ReturnData(encoded_text, code_objects) 

def decode(data: ReturnData, need_to_print = False) -> str: #Просто ищем подходящий нам код, так как прямой Фано, то идём в прямом порядку по закодированному тексту
    codes_dict = {code_obj.code : code_obj.letter for code_obj in data.codes}

    decoded_text = ""
    current_code = ""
    
    for i in data.encoded_text:
        current_code += i
        
        if current_code in codes_dict.keys():
            found_char = codes_dict[current_code]
            decoded_text+=found_char
            current_code = ""
            if(need_to_print):
                print(f'Найден код: {current_code}, ему соответствует {'Символ пробела' if found_char == ' ' else found_char}')
                print(f'Текст на данный момент: {decoded_text}')
    
    
    return decoded_text


def main():
    text_type = 'small_text.txt'
    with open(text_type, 'r') as file:
        text = file.read()
        encoded_text = encode(text, False).encoded_text
        print('Маленький текст')
        print(f"Количество информации исходного текста: {len(text) * 8} бит")
        print(f"Количество информации закодированного текста: {len(encoded_text)} бит")

    text_type = 'large_text.txt'
    with open(text_type, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
        encoded_text = encode(text, False).encoded_text
        print('Большой текст')
        print(f"Количество информации исходного текста: {len(text) * 8} бит")
        print(f"Количество информации закодированного текста: {len(encoded_text)} бит")

if __name__ == "__main__":
    main()