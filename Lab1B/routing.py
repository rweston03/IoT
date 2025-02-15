# Routing - can be done at same time as mapping, needs mapping for testing, needs to be done before navigation

# Adding code from Red Blob Games source "Implementation of A*" 
# found on https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar, https://www.redblobgames.com/pathfinding/a-star/implementation.py
# TODO: modify to match our maps when mapping step is done
from mapping import GridLocation, SquareGrid
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
import collections
import heapq

T = TypeVar('T')

class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]

def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from: dict[GridLocation, GridLocation],
                     start: GridLocation, goal: GridLocation) -> list[GridLocation]:

    current: GridLocation = goal
    path: list[GridLocation] = []
    if goal not in came_from: # no path was found
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path

def a_star_search(graph: SquareGrid, start: GridLocation, goal: GridLocation):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[GridLocation, Optional[GridLocation]] = {}
    cost_so_far: dict[GridLocation, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: GridLocation = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
    
    return reconstruct_path(came_from, start, goal)


