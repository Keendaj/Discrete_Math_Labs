from my_dataclasses import Code, ReturnData
from typing import List, Tuple
import struct
import random
import os
import time

class TreeNode:
    def __init__(self, char=None):
        self.char = char
        self.left = None
        self.right = None

    def is_leaf(self):
        return self.left is None and self.right is None

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

def build_tree_from_codes(codes: List[Tuple[str, str]]) -> TreeNode:
    '''
    Строим бинарное дерево из готовых кодов
    '''
    root = TreeNode()
    
    for char, code in codes:
        current_node = root
        for bit in code:
            if bit == '0':
                if current_node.left is None:
                    current_node.left = TreeNode()
                current_node = current_node.left
            else:
                if current_node.right is None:
                    current_node.right = TreeNode()
                current_node = current_node.right
        current_node.char = char
    
    return root

def generate_codes_from_tree(root: TreeNode, current_code: str = '', codes_dict: dict = None) -> dict:
    if codes_dict is None:
        codes_dict = {}

    if root is None:
        return codes_dict

    if root.is_leaf():
        codes_dict[root.char] = current_code
    else:
        generate_codes_from_tree(root.left, current_code + '0', codes_dict)
        generate_codes_from_tree(root.right, current_code + '1', codes_dict)

    return codes_dict

def serialize_tree(root: TreeNode) -> bytes:
    '''
    Сериализуем дерево в бинарный формат
    '''
    if root is None:
        return b''

    result = bytearray()

    def preorder_traversal(node: TreeNode):
        if node is None:
            return

        if node.is_leaf():
            result.append(0) 
            char_byte = ord(node.char)
            result.append(char_byte)
        else:
            result.append(1)

        preorder_traversal(node.left)
        preorder_traversal(node.right)

    preorder_traversal(root)
    return bytes(result)


def deserialize_tree(data: bytes) -> TreeNode:
    '''
    Десериализуем дерево из бинарного формата
    '''
    if not data:
        return None

    class Index:
        def __init__(self):
            self.value = 0

    idx = Index()
    idx.value = 0

    def build_tree() -> TreeNode:
        if idx.value >= len(data):
            return None

        flag = data[idx.value]
        idx.value += 1

        if flag == 0:
            char_code = data[idx.value]
            idx.value += 1
            char = chr(char_code)
            return TreeNode(char)
        else:
            node = TreeNode()
            node.left = build_tree()
            node.right = build_tree()
            return node

    return build_tree()


def text_to_binary(encoded_text: str) -> tuple[bytes, int]:
    padding = 8 - (len(encoded_text) % 8)
    if padding != 8:
        encoded_text += '0' * padding

    binary_data = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte_str = encoded_text[i:i + 8]
        byte_val = int(byte_str, 2)
        binary_data.append(byte_val)

    return bytes(binary_data), padding


def binary_to_text(binary_data: bytes, padding: int, original_length: int) -> str:
    binary_string = ''
    for byte in binary_data:
        binary_string += format(byte, '08b')

    if padding != 8:
        binary_string = binary_string[:-padding]

    if original_length > 0:
        binary_string = binary_string[:original_length]

    return binary_string

def encode(filename: str, need_to_print=False):
    '''
    Кодируем текст с помощью кода Фано
    '''
    text = ""
    with open(filename, 'rb') as file:
        data = file.read()
        original_bits = len(data) * 8
        text = data.decode('utf-8')

    frequencies = count_quantity(text)
    codes = [[i[0], ''] for i in frequencies]

    def make_fano_code(start: int, end: int, current_code: str) -> None:
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
        encoded_text += codes_dict[i]

    root = build_tree_from_codes(codes)

    tree_filename = filename.replace('.txt', '_codetree.bin')
    tree_data = serialize_tree(root)
    with open(tree_filename, 'wb') as tree_file:
        tree_file.write(struct.pack('B', len(tree_data)))
        tree_file.write(tree_data)

    encoded_filename = filename.replace('.txt', '_encoded.bin')
    binary_encoded, padding = text_to_binary(encoded_text)
    with open(encoded_filename, 'wb') as encoded_file:
        encoded_file.write(struct.pack('B', padding))
        encoded_file.write(binary_encoded)


def decode(tree_filename: str, encoded_filename: str, need_to_print=False):
    '''
    Декодируем текст и записываем результат в файл
    '''
    with open(tree_filename, 'rb') as tree_file:
        tree_len = struct.unpack('B', tree_file.read(1))[0]
        tree_data = tree_file.read(tree_len)
        root = deserialize_tree(tree_data)

    with open(encoded_filename, 'rb') as encoded_file:
        padding = struct.unpack('B', encoded_file.read(1))[0]
        binary_data = encoded_file.read()

    original_length = len(binary_data) * 8 - padding
    encoded_text = binary_to_text(binary_data, padding, original_length)

    decoded_text = ""
    current_node = root
    for bit in encoded_text:
        if bit == '0':
            if need_to_print:
                print("0", end =" ")
            current_node = current_node.left
        else:
            if need_to_print:
                print("1", end =" ")
            current_node = current_node.right

        if current_node and current_node.is_leaf():
            found_char = current_node.char
            decoded_text += found_char
            if need_to_print:
                print(f"Найден символ: {'Символ пробела' if found_char == ' ' else found_char}")
            current_node = root
        
    decoded_filename = encoded_filename.replace('_encoded.bin', '_decoded.txt')
    with open(decoded_filename, 'wb') as decoded_file:
        decoded_file.write(decoded_text.encode('utf-8'))
        print(f"Декодированный текст сохранён в {decoded_filename}")

def generate_ascii_text(num_words, filename):
    """
    Генерирует чисто ASCII текст с заданным количеством слов
    """
    words = [
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
        'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
        'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
        'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
        'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
        'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
        'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
        'is', 'are', 'was', 'were', 'has', 'had', 'been', 'have', 'did', 'done',
        'say', 'said', 'says', 'go', 'went', 'gone', 'get', 'got', 'gotten', 'make',
        'made', 'know', 'known', 'think', 'thought', 'see', 'saw', 'seen', 'come', 'came',
        'look', 'looked', 'use', 'used', 'find', 'found', 'give', 'gave', 'given', 'tell',
        'told', 'ask', 'asked', 'work', 'worked', 'seem', 'seemed', 'feel', 'felt', 'try',
        'tried', 'leave', 'left', 'call', 'called', 'need', 'needed', 'become', 'became', 'put'
    ]
    punctuation = ['.', ',', '!', '?', ';', ':']
    
    sentences = []
    words_used = 0
    
    while words_used < num_words:
        sentence_length = random.randint(5, 15)
        if words_used + sentence_length > num_words:
            sentence_length = num_words - words_used
        
        sentence_words = []
        for i in range(sentence_length):
            word = random.choice(words)
            sentence_words.append(word)

        if random.random() < 0.7:
            sentence_words[-1] += random.choice(['.', '.', '.', '!', '?'])
        else:
            sentence_words[-1] += '.'
        
        sentences.append(' '.join(sentence_words))
        words_used += sentence_length
    
    text = ' '.join(sentences)

    with open(filename, 'w', encoding='ascii') as f:
        f.write(text)
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        print("✗ Ошибка: найден не-ASCII символ")

def main():
    generate_ascii_text(500, 'medium_text.txt')
    generate_ascii_text(1500, 'large_text.txt')

    print("Программа для сжатия и распаковки файлов")
    print("Доступные команды:")
    print("  compress <filename> [--show] - сжать файл (--show для отображения дерева кодов)")
    print("  decompress <tree_file> <encoded_file> [--show] - распаковать файл (--show для отображения дерева кодов)")
    print("  exit                   - выйти из программы")
    print()
    
    while True:
        try:
            command = input("Введите команду: ").strip().split()
            
            if not command:
                continue
                
            if command[0] == "exit":
                print("Выход из программы...")
                break
                
            elif command[0] == "compress":
                if len(command) < 2:
                    print("Ошибка: Используйте: compress <filename> [--show]")
                    continue
                    
                filename = command[1]
                show_tree = "--show" in command
                
                if not os.path.exists(filename):
                    print(f"Ошибка: Файл '{filename}' не найден")
                    continue
                    
                try:
                    encode(filename, show_tree)
                    
                    original_size = os.path.getsize(filename)
                    tree_filename = filename.replace('.txt', '_codetree.bin')
                    encoded_filename = filename.replace('.txt', '_encoded.bin')
                    tree_size = os.path.getsize(tree_filename)
                    encoded_size = os.path.getsize(encoded_filename)
                    
                    print(f"\nСжатие завершено успешно!")
                    print(f"Исходный размер: {original_size} байт")
                    print(f"Размер дерева кодов: {tree_size} байт")
                    print(f"Размер сжатого текста: {encoded_size} байт")
                    print(f"Общий размер после сжатия: {tree_size + encoded_size} байт")
                    print(f"Коэффициент сжатия: {(1 - (tree_size + encoded_size) / original_size) * 100:.2f}%")
                    print(f"Созданы файлы: {tree_filename}, {encoded_filename}")
                    
                except Exception as e:
                    print(f"Ошибка при сжатии: {e}")
                    
            elif command[0] == "decompress":
                if len(command) < 3:
                    print("Ошибка: Используйте: decompress <tree_file> <encoded_file> [--show]")
                    continue
                    
                tree_file = command[1]
                encoded_file = command[2]
                show_tree = "--show" in command
                
                if not os.path.exists(tree_file):
                    print(f"Ошибка: Файл дерева '{tree_file}' не найден")
                    continue
                    
                if not os.path.exists(encoded_file):
                    print(f"Ошибка: Сжатый файл '{encoded_file}' не найден")
                    continue
                    
                try:
                    base_name = tree_file.replace('_codetree.bin', '')
                    if base_name == tree_file:
                        base_name = encoded_file.replace('_encoded.bin', '')
                    
                    decode(tree_file, encoded_file, show_tree)
                    
                    decoded_file = base_name + '_decoded.txt'
                    print(f"\nРаспаковка завершена успешно!")
                    print(f"Создан файл: {decoded_file}")

                    original_file = base_name + '.txt'
                    if os.path.exists(original_file):
                        with open(original_file, 'r', encoding='ascii') as f:
                            original_text = f.read()
                        with open(decoded_file, 'r', encoding='ascii') as f:
                            decoded_text = f.read()
                        
                        if original_text == decoded_text:
                            print("Целостность данных проверена: файлы идентичны")
                        else:
                            print("Предупреждение: распакованный файл отличается от исходного")
                    
                except Exception as e:
                    print(f"Ошибка при распаковке: {e}")
                    
            else:
                print("Ошибка: Неизвестная команда. Доступные команды: compress, decompress, exit")
                
        except KeyboardInterrupt:
            print("\n\nВыход из программы...")
            break
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()