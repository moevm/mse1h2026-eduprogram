from typing import Dict

def dfs(node: str, graph: Dict[str, list], usedNodesDFS: Dict[str, bool], visited: set = set()):
    usedNodesDFS[node] = True
    childs = graph[node].copy()
    visited.add(node)
    for child in childs:
        if usedNodesDFS[child]:
            continue
        graph[node].remove(child)
        usedNodesDFS[child] = True
        visited.add(child)
        dfs(child, graph, usedNodesDFS, visited)


def find_bridges(graph: Dict[str, list]):
    usedNodesDFS1 = {}
    usedNodesDFS2 = {}
    for node in graph.keys():
        usedNodesDFS1[node] = False
        usedNodesDFS2[node] = False

    graphAfterDFS = graph.copy()
    nodes = list(graphAfterDFS.keys())
    if len(nodes) == 0:
        return []
    dfs(nodes[0], graphAfterDFS, usedNodesDFS1)
    bridges = []
    groups = []
    while True:
        isAnyUnused = False
        for node in usedNodesDFS2.keys():
            if not usedNodesDFS2[node]:
                isAnyUnused = True
                visited = set()
                dfs(node, graphAfterDFS, usedNodesDFS2, visited)
                groups.append(visited)
                break
        if not isAnyUnused:
            break

    for group in groups:
        for node in group:
            resultNodes = set(graph[node]) - group
            for el in resultNodes:
                bridges.append((node, el))

    return bridges


# if __name__ == "__main__":
#     data = {
#         "A": ["B", "C"],
#         "B": ["A", "D"],
#         "C": ["A", "D"],
#         "D": ["B", "C", "E"],
#         "E": ["D", "F", "G"],
#         "F": ["E"],
#         "G": ["E"]
#     }
#     print(find_bridges(data))