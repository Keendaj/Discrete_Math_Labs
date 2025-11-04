from collections import deque

def find_cycle(graph):
    """Поиск одного цикла через BFS. Возвращает список вершин в порядке цикла."""
    n = len(graph)
    visited = [False] * n
    parent = [-1] * n

    for start in range(n):
        if not visited[start]:
            queue = deque([start])
            visited[start] = True

            while queue:
                node = queue.popleft()
                for neighbor in graph[node]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        parent[neighbor] = node
                        queue.append(neighbor)
                    elif parent[node] != neighbor:
                        path_node = []
                        cur = node
                        while cur != -1:
                            path_node.append(cur)
                            cur = parent[cur]
                        path_node_set = set(path_node)

                        path_neighbor = []
                        cur = neighbor
                        while cur not in path_node_set:
                            path_neighbor.append(cur)
                            cur = parent[cur]

                        path_neighbor.append(cur)

                        path_node = path_node[:path_node.index(cur)+1]
                        cycle = path_node + path_neighbor[::-1][1:]
                        cycle.append(cycle[0])
                        return cycle
    return None



def is_acyclic(graph):
    """Проверка ацикличности"""
    cycle = find_cycle(graph)
    return (cycle is None), cycle


def path_exists(graph, start, end):
    """Проверка существования пути между вершинами."""
    queue = deque([start])
    visited = [False] * len(graph)
    visited[start] = True

    while queue:
        node = queue.popleft()
        if node == end:
            return True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                queue.append(neighbor)
    return False


def check_subcyclicity(graph):
    """
    Проверка субцикличности: для каждого отсутствующего ребра должен существовать путь."""
    n = len(graph)
    edges = set()
    for u in range(n):
        for v in graph[u]:
            if u < v:
                edges.add((u, v))

    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in edges:
                if not path_exists(graph, u, v):
                    return False, (u, v)
    return True, None


def check_tree_properties(graph):
    """Проверка свойств дерева: выводим только нарушения."""
    n = len(graph)
    m = sum(len(adj) for adj in graph) // 2

    acyclic, cycle = is_acyclic(graph)
    subcyclic, bad_edge = check_subcyclicity(graph)
    tree_like = (m == n - 1)

    result = []
    result.append(f"Вершин: {n}, Рёбер: {m}")

    if not acyclic:
        result.append("Нарушена ацикличность.")
        if cycle:
            result.append(f"   Найден цикл: {cycle}")

    if not subcyclic:
        result.append("Нарушена субцикличность.")
        result.append(f"   Пример ребра, нарушающего свойство: {bad_edge}")

    if not tree_like:
        result.append("Нарушена древочисленность (|E| ≠ |V| - 1).")

    if acyclic and subcyclic and tree_like:
        result.append("Граф является деревом (все свойства выполнены).")

    return "\n".join(result)



def read_graph_from_file(filename):
    """Читает граф из файла формата:
       n m
       u1 v1
       u2 v2
    """
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    n, m = map(int, lines[0].split())
    graph = [[] for _ in range(n)]

    for line in lines[1:]:
        u, v = map(int, line.split())
        if max(u, v) > n - 1:
            u -= 1
            v -= 1
        graph[u].append(v)
        graph[v].append(u)
    return graph


def write_output_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == "__main__":
    print("Введите команду (пример: check input.txt output.txt), для выхода exit")
    while True:
        try:
            cmd = input("> ").strip().split()
            if len(cmd) == 0:
                continue
            if cmd[0].lower() == "exit":
                print("Выход из программы.")
                break
            elif cmd[0].lower() == "check":
                if len(cmd) != 3:
                    print("❌ Неверный формат. Используйте: check input.txt output.txt")
                    continue
                input_file, output_file = cmd[1], cmd[2]
                try:
                    graph = read_graph_from_file(input_file)
                    result = check_tree_properties(graph)
                    write_output_to_file(output_file, result)
                    print(f"✅ Проверка завершена. Результат записан в {output_file}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            else:
                print("Неизвестная команда. Используйте 'check' или 'exit'.")
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break