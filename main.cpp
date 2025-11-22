#include <iostream>
#include <fstream>
#include <vector>
#include <list>
#include <algorithm>
#include <string>
#include <memory>
#include <stack>

class Graph {
private:
    int vertices;
    std::vector<std::list<int>> adjList;
    std::vector<std::pair<int, int>> edges;

    void DFSIterative(int start, std::vector<bool>& visited) {
        std::stack<int> stack;
        stack.push(start);
        visited[start] = true;

        while (!stack.empty()) {
            int current = stack.top();
            stack.pop();

            for (auto neighbor : adjList[current]) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    stack.push(neighbor);
                }
            }
        }
    }

    bool isConnected() {
        if (vertices == 0) return true;
        
        std::vector<bool> visited(vertices, false);
        int startVertex = -1;
        
        for (int i = 0; i < vertices; i++) {
            if (!adjList[i].empty()) {
                startVertex = i;
                break;
            }
        }
        
        if (startVertex == -1) return true;
        
        DFSIterative(startVertex, visited);
        
        for (int i = 0; i < vertices; i++) {
            if (!adjList[i].empty() && !visited[i]) {
                return false;
            }
        }
        return true;
    }

    bool hasVertexWithDegreeOne() {
        for (int i = 0; i < vertices; i++) {
            if (adjList[i].size() == 1) {
                return true;
            }
        }
        return false;
    }

    bool isSafe(int v, const std::vector<int>& path, int pos) {
        if (std::find(adjList[path[pos - 1]].begin(), 
                      adjList[path[pos - 1]].end(), v) == adjList[path[pos - 1]].end()) {
            return false;
        }
        
        return std::find(path.begin(), path.begin() + pos, v) == path.begin() + pos;
    }

    bool hamCycleIterative(std::vector<int>& path) {
        struct State {
            int pos;
            int nextVertexToTry;
            std::vector<int> currentPath;
        };
        
        std::stack<State> stack;
        
        State initialState;
        initialState.pos = 1;
        initialState.nextVertexToTry = 1;
        initialState.currentPath = path;
        
        stack.push(initialState);
        
        while (!stack.empty()) {
            State currentState = stack.top();
            stack.pop();
            
            int pos = currentState.pos;
            std::vector<int> currentPath = currentState.currentPath;
            
            if (pos == vertices) {
                if (std::find(adjList[currentPath[pos - 1]].begin(),
                            adjList[currentPath[pos - 1]].end(), currentPath[0]) != adjList[currentPath[pos - 1]].end()) {
                    path = currentPath;
                    return true;
                }
                continue;
            }
            
            for (int v = currentState.nextVertexToTry; v < vertices; v++) {
                if (isSafe(v, currentPath, pos)) {
                    State newState;
                    newState.pos = pos + 1;
                    newState.nextVertexToTry = 1;
                    newState.currentPath = currentPath;
                    newState.currentPath[pos] = v;
                    
                    State backtrackState;
                    backtrackState.pos = pos;
                    backtrackState.nextVertexToTry = v + 1;
                    backtrackState.currentPath = currentPath;
                    
                    stack.push(backtrackState);
                    stack.push(newState);
                    break;
                }
            }
        }
        
        return false;
    }

public:
    Graph(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + filename);
        }

        int n;
        file >> n;
        edges.resize(n);
        int maxVertex = 0;

        for (int i = 0; i < n; i++) {
            file >> edges[i].first >> edges[i].second;
            maxVertex = std::max(maxVertex, std::max(edges[i].first, edges[i].second));
        }
        
        vertices = maxVertex + 1;
        adjList.resize(vertices);

        for (const auto& edge : edges) {
            adjList[edge.first].push_back(edge.second);
            adjList[edge.second].push_back(edge.first);
        }
        file.close();
    }

    std::vector<int> findHamiltonianCycle() {
        // Этап 1: Проверка связности
        if (!isConnected()) {
            std::cout << "Граф несвязный - гамильтонов цикл невозможен" << std::endl;
            return {};
        }

        // Этап 2: Проверка вершин со степенью 1
        if (hasVertexWithDegreeOne()) {
            std::cout << "Найдена вершина со степенью 1 - гамильтонов цикл невозможен" << std::endl;
            return {};
        }

        // Этап 3: Итеративный бэктрекинг
        std::vector<int> path(vertices, -1);
        path[0] = 0;

        std::cout << "Запуск итеративного поиска гамильтонова цикла..." << std::endl;
        
        if (!hamCycleIterative(path)) {
            std::cout << "Гамильтонов цикл не найден" << std::endl;
            return {};
        }

        std::cout << "Гамильтонов цикл найден!" << std::endl;
        return path;
    }

    void printCycle(const std::vector<int>& cycle, std::ostream& os = std::cout) {
        if (cycle.empty()) {
            os << "Гамильтонов цикл не найден" << std::endl;
            return;
        }

        os << "Гамильтонов цикл (" << cycle.size() << " вершин): ";
        for (size_t i = 0; i < cycle.size(); i++) {
            os << cycle[i];
            if (i < cycle.size() - 1) os << " -> ";
        }
        os << " -> " << cycle[0] << std::endl;
    }

    void printGraphInfo(std::ostream& os = std::cout) {
        os << "Информация о графе:" << std::endl;
        os << "Количество вершин: " << vertices << std::endl;
        os << "Количество ребер: " << edges.size() << std::endl;
        os << "Список смежности:" << std::endl;
        
        for (int i = 0; i < vertices; i++) {
            if (!adjList[i].empty()) {
                os << "Вершина " << i << ": ";
                for (int neighbor : adjList[i]) {
                    os << neighbor << " ";
                }
                os << std::endl;
            }
        }
    }
};

void printMenu() {
    std::cout << "\n=== Меню поиска гамильтонова цикла ===" << std::endl;
    std::cout << "1. Загрузить граф и найти гамильтонов цикл" << std::endl;
    std::cout << "2. Выйти" << std::endl;
    std::cout << "Выберите опцию: ";
}

void processGraph(const std::string& filename) {
    try {
        Graph graph(filename);
        
        std::cout << "\nГраф успешно загружен из файла: " << filename << std::endl;
        graph.printGraphInfo();
        
        std::cout << "\nПоиск гамильтонова цикла..." << std::endl;
        auto cycle = graph.findHamiltonianCycle();
        
        if (!cycle.empty()) {
            std::cout << "\nРезультат:" << std::endl;
            graph.printCycle(cycle);
            
            std::string outputFile = "result_" + filename;
            std::ofstream out(outputFile);
            if (out.is_open()) {
                graph.printCycle(cycle, out);
                out.close();
                std::cout << "Результат сохранен в файл: " << outputFile << std::endl;
            } else {
                std::cout << "Не удалось сохранить результат в файл" << std::endl;
            }
        }
        
    } catch (const std::exception& e) {
        std::cout << "Ошибка: " << e.what() << std::endl;
    }
}

int main() {
    std::cout << "Программа поиска гамильтонова цикла в графе" << std::endl;
    
    while (true) {
        printMenu();
        int choice;
        std::cin >> choice;

        switch (choice) {
            case 1: {
                std::string filename;
                std::cout << "Введите имя файла с графом: ";
                std::cin >> filename;
                processGraph(filename);
                break;
            }
            case 2:
                std::cout << "Выход из программы..." << std::endl;
                return 0;
            default:
                std::cout << "Неверный выбор! Попробуйте снова." << std::endl;
        }
    }
    
    return 0;
}