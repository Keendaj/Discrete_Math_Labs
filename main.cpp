#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <queue>
#include <stack>
#include <algorithm>
#include <cstdlib>
#include <iomanip>
#include <set>

class BipartiteGraph {
private:
    // исходные данные
    std::vector<std::pair<int,int>> edges; // список рёбер

    // после загрузки
    int nLeft = 0;
    int nRight = 0;
    std::vector<int> leftId;   // leftId[orig] = index в [1..nLeft] или 0
    std::vector<int> rightId;  // rightId[orig] = index в [1..nRight] или 0
    std::vector<int> leftOrig; // leftOrig[idx] = оригинальный номер вершины
    std::vector<int> rightOrig;// rightOrig[idx] = оригинальный номер вершины
    std::vector<std::vector<int>> adj; // adj[leftIndex] -> список rightIndex

    // для паросочетания
    std::vector<int> matchRight; // matchRight[r] = leftIndex или 0 (free)
    bool maxMatchingFound = false;
    int matchCount = 0;

public:
    BipartiteGraph() {}

    bool loadFromFile(const std::string& filename) {
        std::ifstream fin(filename);
        if (!fin.is_open()) {
            std::cerr << "Ошибка: не удалось открыть файл " << filename << "\n";
            return false;
        }

        edges.clear();
        
        int m = 0;
        if (!(fin >> m)) {
            std::cerr << "Ошибка: неверный формат файла (ожидается 'm' в первой строке).\n";
            fin.close();
            return false;
        }

        int u, v;
        for (int i = 0; i < m; ++i) {
            if (!(fin >> u >> v)) {
                std::cerr << "Ошибка: ожидается " << m << " рёбер, файл закончился раньше.\n";
                fin.close();
                return false;
            }
            if (u <= 0 || v <= 0) {
                std::cerr << "Ошибка: номера вершин должны быть положительными целыми числами\n";
                fin.close();
                return false;
            }
            edges.emplace_back(u, v);
        }
        fin.close();

        buildBipartiteStructure();

        std::cout << "✅ Файл загружен. Левая доля: " << nLeft 
                  << ", правая доля: " << nRight 
                  << ", рёбер: " << edges.size() << "\n";
        return true;
    }

    void buildBipartiteStructure() {
        std::set<int> leftSet, rightSet;
        
        for (auto &e : edges) {
            leftSet.insert(e.first);
            rightSet.insert(e.second);
        }

        nLeft = leftSet.size();
        nRight = rightSet.size();

        // сброс предыдущего состояния
        leftId.clear();
        rightId.clear();
        leftOrig.clear();
        rightOrig.clear();
        adj.clear();
        matchRight.clear();
        maxMatchingFound = false;
        matchCount = 0;

        matchRight.assign(nRight + 1, 0);

        leftOrig.push_back(0);
        int index = 1;
        for (int vertex : leftSet) {
            leftOrig.push_back(vertex);
            if (vertex >= (int)leftId.size()) {
                leftId.resize(vertex + 1, 0);
            }
            leftId[vertex] = index++;
        }

        rightOrig.push_back(0);
        index = 1;
        for (int vertex : rightSet) {
            rightOrig.push_back(vertex);
            if (vertex >= (int)rightId.size()) {
                rightId.resize(vertex + 1, 0);
            }
            rightId[vertex] = index++;
        }

        adj.assign(nLeft + 1, {});
        for (auto &e : edges) {
            int u = e.first;
            int v = e.second;
            
            if (leftId[u] == 0) {
                std::cerr << "Ошибка: вершина " << u << " не найдена в левой доле\n";
                continue;
            }
            if (rightId[v] == 0) {
                std::cerr << "Ошибка: вершина " << v << " не найдена в правой доле\n";
                continue;
            }
            
            adj[leftId[u]].push_back(rightId[v]);
        }
    }

    bool tryKuhn(int start) {
        std::vector<char> usedL(nLeft + 1, 0);
        std::vector<char> usedR(nRight + 1, 0);

        std::vector<int> stack;
        std::vector<int> edgeIndex(nLeft + 1, 0);
        std::vector<int> parentR(nRight + 1, -1);
        std::vector<int> parentL(nLeft + 1, -1);
        std::vector<int> chosenRight(nLeft + 1, -1);

        stack.push_back(start);
        usedL[start] = 1;
        parentL[start] = -1;
        chosenRight[start] = -1;

        while (!stack.empty()) {
            int v = stack.back();

            if (edgeIndex[v] >= (int)adj[v].size()) {
                stack.pop_back();
                continue;
            }

            int to = adj[v][edgeIndex[v]++];
            if (usedR[to]) continue;
            usedR[to] = 1;

            chosenRight[v] = to;
            parentR[to] = v;

            if (matchRight[to] == 0) {
                int curR = to;
                while (curR != -1) {
                    int curL = parentR[curR];
                    int prevR = parentL[curL];
                    matchRight[curR] = curL;
                    curR = prevR;
                }
                return true;
            } else {
                int pairedL = matchRight[to];
                if (!usedL[pairedL]) {
                    usedL[pairedL] = 1;
                    parentL[pairedL] = to;
                    stack.push_back(pairedL);
                }
            }
        }

        return false;
    }

    void findMaximumMatching() {
        if (nLeft == 0 || nRight == 0) {
            std::cout << "Сначала загрузите граф из файла.\n";
            return;
        }

        if (!maxMatchingFound) {
            matchRight.assign(nRight + 1, 0); // 0 = free
            matchCount = 0;

            for (int u = 1; u <= nLeft; ++u) {
                bool inMatching = false;
                for (int r = 1; r <= nRight; ++r) if (matchRight[r] == u) { inMatching = true; break; }
                if (!inMatching) {
                    if (tryKuhn(u)) matchCount++;
                }
            }

            maxMatchingFound = true;
        }

        std::cout << "\n🔹 Найдено паросочетание размера " << matchCount << "\n";
        printMaxMatching();
    }

    void printMaxMatching() {
        for (int r = 1; r <= nRight; ++r) {
            if (matchRight[r] != 0) {
                int l = matchRight[r];
                std::cout << "  L" << leftOrig[l] << " -> R" << rightOrig[r] << "\n";
            }
        }
    }

    void exportToPNG(const std::string& filename = "graph.png") {
        if (nLeft == 0 || nRight == 0) {
            std::cout << "Сначала загрузите граф!\n";
            return;
        }

        if (matchRight.empty()) {
            matchRight.assign(nRight + 1, 0);
        }

        std::ofstream fout("graph.dot");
        fout << "graph G {\n";
        fout << "  rankdir=LR;\n";
        fout << "  node [shape=circle, style=filled, fillcolor=lightgray];\n";
        fout << "  subgraph cluster_left {\n";
        fout << "    label=\"Левая доля\";\n";
        fout << "    color=lightblue;\n";
        for (int i = 1; i <= nLeft; ++i) {
            fout << "    L" << leftOrig[i] << " [fillcolor=lightblue, label=\"L" << leftOrig[i] << "\"];\n";
        }
        fout << "  }\n";
        fout << "  subgraph cluster_right {\n";
        fout << "    label=\"Правая доля\";\n";
        fout << "    color=lightgreen;\n";
        for (int j = 1; j <= nRight; ++j) {
            fout << "    R" << rightOrig[j] << " [fillcolor=lightgreen, label=\"R" << rightOrig[j] << "\"];\n";
        }
        fout << "  }\n";

        for (auto &e : edges) {
            int u = e.first, v = e.second;
            int li = leftId[u];
            int ri = rightId[v];
            
            if (li <= 0 || li > nLeft || ri <= 0 || ri > nRight) {
                continue;
            }
            
            bool inMatch = (matchRight[ri] == li);
            fout << "  L" << u << " -- R" << v;
            if (inMatch) fout << " [color=red, penwidth=3]";
            fout << ";\n";
        }

        fout << "}\n";
        fout.close();

        std::cout << "Создан graph.dot. Генерируется PNG...\n";
        std::string cmd = "dot -Tpng graph.dot -o " + filename;
        int res = system(cmd.c_str());
        if (res == 0) std::cout << "✅ Граф сохранён в " << filename << "\n";
        else std::cout << "⚠️ Не удалось вызвать Graphviz (dot). Установите graphviz и проверьте PATH.\n";
    }
};

void showMenu() {
    std::cout << "\n==============================\n";
    std::cout << " 1. Загрузить граф из файла (первая строка: m, далее m строк 'u v')\n";
    std::cout << " 2. Найти паросочетание\n";
    std::cout << " 3. Сохранить граф в PNG (graph.png)\n";
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
        if (!(std::cin >> choice)) break;
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