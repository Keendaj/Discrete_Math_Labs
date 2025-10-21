#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <iomanip>
#include <cstdlib>

class BipartiteGraph {
private:
    int n, m, maxRight;
    std::vector<std::vector<int>> adj;
    std::vector<int> matchRight;
    bool maxMatchingFounded = false;
    int matchCount = 0;

public:
    BipartiteGraph() : n(0), m(0), maxRight(0) {}

    bool loadFromFile(const std::string& filename) {
        std::ifstream fin(filename);
        if (!fin.is_open()) {
            std::cerr << "Ошибка: не удалось открыть файл " << filename << "\n";
            return false;
        }
        fin >> n >> m;
        adj.assign(n + 1, {});
        int a, b;
        maxRight = 0;
        for (int i = 0; i < m; ++i) {
            fin >> a >> b;
            adj[a].push_back(b);
            if (b > maxRight) maxRight = b;
        }
        fin.close();
        std::cout << "✅ Граф загружен. Левых вершин: " << n << ", правых: " << maxRight << "\n";
        return true;
    }

    bool tryKuhn(int start) {
        std::vector<int> stack;
        std::vector<int> edgeIndex(n + 1, 0);
        std::vector<int> parent(n + 1, -1);
        std::vector<bool> visited(n + 1, false);

        stack.push_back(start);

        while (!stack.empty()) {
            int v = stack.back();
            if (!visited[v]) {
                visited[v] = true;
            }

            bool advanced = false;
            while (edgeIndex[v] < (int)adj[v].size()) {
                int to = adj[v][edgeIndex[v]++];
                if (matchRight[to] == -1) {
                    while (!stack.empty()) {
                        int cur = stack.back();
                        stack.pop_back();
                        matchRight[to] = cur;
                        to = -1;
                        if (!stack.empty()) to = adj[stack.back()][edgeIndex[stack.back()] - 1];
                    }
                    return true;
                } else if (!visited[matchRight[to]]) {
                    parent[matchRight[to]] = v;
                    stack.push_back(matchRight[to]);
                    advanced = true;
                    break;
                }
            }

            if (!advanced) {
                stack.pop_back();
            }
        }
        return false;
    }

    void findMaximumMatching() {
        if (!maxMatchingFounded) {
            matchRight.assign(maxRight + 1, -1);
            for (int v = 1; v <= n; ++v) {
                if (tryKuhn(v)) matchCount++;
            }
            maxMatchingFounded = true;
        }

        std::cout << "\n🔹 Найдено паросочетание размером " << matchCount << "\n";
        printMaxMatching();
    }

    void printMaxMatching() {
        for (int j = 1; j <= maxRight; ++j) {
            if (matchRight[j] != -1)
                std::cout << "  L" << matchRight[j] << " → R" << j << "\n";
        }
    }

    void exportToPNG(const std::string& filename = "graph.png") const {
        if (n == 0) {
            std::cout << "Сначала загрузите граф!\n";
            return;
        }

        std::ofstream fout("graph.dot");
        fout << "graph G {\n";
        fout << "  rankdir=LR;\n";
        fout << "  node [shape=circle, style=filled, fillcolor=lightgray];\n";
        fout << "  subgraph cluster_left {\n";
        fout << "    label=\"Левая доля\";\n";
        fout << "    color=lightblue;\n";
        for (int i = 1; i <= n; ++i)
            fout << "    L" << i << " [fillcolor=lightblue];\n";
        fout << "  }\n";
        fout << "  subgraph cluster_right {\n";
        fout << "    label=\"Правая доля\";\n";
        fout << "    color=lightgreen;\n";
        for (int j = 1; j <= maxRight; ++j)
            fout << "    R" << j << " [fillcolor=lightgreen];\n";
        fout << "  }\n";

        for (int i = 1; i <= n; ++i)
            for (int to : adj[i])
                fout << "  L" << i << " -- R" << to << ";\n";

        fout << "}\n";
        fout.close();

        std::cout << "Создан файл graph.dot. Генерируется PNG...\n";
        std::string cmd = "dot -Tpng graph.dot -o " + filename;
        int res = system(cmd.c_str());
        if (res == 0)
            std::cout << "✅ Граф успешно сохранён в " << filename << "\n";
        else
            std::cout << "⚠️ Не удалось вызвать Graphviz. Проверьте, установлен ли `dot`.\n";
    }
};

void showMenu() {
    std::cout << "\n==============================\n";
    std::cout << " 1. Загрузить граф\n";
    std::cout << " 2. Найти паросочетание\n";
    std::cout << " 3. Сохранить граф в PNG\n";
    std::cout << " 4. Выход\n";
    std::cout << "==============================\n";
    std::cout << "Ваш выбор: ";
}

int main() {
    setlocale(LC_ALL, "Russian");
    BipartiteGraph graph;
    std::string filename;
    int choice;

    while (true) {
        showMenu();
        std::cin >> choice;
        if (choice == 1) {
            std::cout << "Введите имя файла: ";
            std::cin >> filename;
            graph.loadFromFile(filename);
        } else if (choice == 2) {
            graph.findMaximumMatching();
        } else if (choice == 3) {
            graph.exportToPNG("graph.png");
        } else if (choice == 4) {
            std::cout << "Выход.\n";
            break;
        } else {
            std::cout << "Некорректный ввод.\n";
        }
    }

    return 0;
}