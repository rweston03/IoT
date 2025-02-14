# Routing - can be done at same time as mapping, needs mapping for testing, needs to be done before navigation

# Adding code from Red Blob Games source "Implementation of A*" 
# found on https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar, https://www.redblobgames.com/pathfinding/a-star/implementation.py
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
import collections
import heapq

T = TypeVar('T')
Location = TypeVar('Location')
GridLocation = Tuple[int, int]

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

def a_star_search(graph: WeightedGraph, start: Location, goal: Location, gridSize: int):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        neighbors = {}
        # Calculate neighbors
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for d in directions:
            if 0 <= d[0] + current[0] < gridSize and 0 <= d[1] + current[1] < gridSize:
                newNeighbor = (d[0] + current[0], d[1] + current[1])
                neighbors[newNeighbor] = graph[newNeighbor[0],newNeighbor[1]]
            
        print(neighbors)
        if current == goal:
            break
        
        for next in neighbors:
            new_cost = cost_so_far[current] + neighbors[next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far
