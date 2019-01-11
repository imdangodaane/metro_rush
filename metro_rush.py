#!/usr/bin/env python3
import collections
from sys import stderr


class Station:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.neighbor = []

    def add_neighbor(self, neighbor_info):
        self.neighbor.append(neighbor_info)

    def add_train(self, train):
        pass


class Line:
    def __init__(self, name):
        self.name = name
        self.stations = []

    def append_city(self, station):
        self.stations.append(station)


class Train:
    def __init__(self, id, current_station):
        self.id = id
        self.name = "T" + str(id)
        self.current_station = current_station

    def move_to(self, next_station):
        self.current_station = next_station


class Map:
    def __init__(self, file_name):
        self.map = []
        self.file_name = file_name
        self.head_hue = ''
        self.tail_hue = ''
        self.head_pos = ''
        self.tail_pos = ''
        self.total_trains = None
        self.station_names = {}
        self.start = ''
        self.end = ''

        content = self.read_file(self.file_name)
        self.create_map(content)
        self.find_neighbor(content)
        self.find_start_and_end()

    def append_line(self, line):
        self.map.append(line)

    def read_file(self, file_name):
        try:
            f = open(file_name, 'r')
            content = f.readlines()
            content = [e.strip() for e in content]
            return content
        except (FileNotFoundError, PermissionError):
            stderr.write('Invalid File')
            exit(1)

    def create_map(self, content):
        # m = Map()
        for i in content:
            if i.startswith('#'):
                line = Line(i[1:])
            elif i[:1].isdigit():
                if ":Conn:" not in i:
                    id, name = i.split(":", 1)
                    station = Station(id,name.strip())
                    line.stations.append(station)
                else:
                    id, name, _, _= i.split(":")
                    station = Station(id,name.strip())
                    line.stations.append(station)
                self.append_line(line)
            elif "=" in i:
                if "START" in i:
                    line_start, position = i.split()
                    _, self.head_hue = line_start.split("=")
                    _, self.head_pos = position.split(":")
                elif  "END" in i:
                    line_end, position = i.split()
                    _, self.tail_hue = line_end.split("=")
                    _, self.tail_pos = position.split(":")
                else:
                    _, self.total_trains = i.split("=")

    def find_neighbor(self, content):
        for i in range(len(content)):
            if content[i][:1].isdigit():
                info = content[i].split(":")
                if len(info) == 2:
                    id, name = info[0], info[1]
                elif len(info) == 4:
                    id, name, _, connect = info[0], info[1], info[2], info[3]
                try:
                    if content[i-1][:1].isdigit():
                        info = content[i-1].split(":")
                        station = Station(info[0],info[1])
                        self.station_names[name].append(station)
                    if content[i+1][:1].isdigit():
                        info = content[i+1].split(":")
                        station = Station(info[0],info[1])
                        self.station_names[name].append(station)
                except IndexError:
                    continue
                except KeyError:
                    self.station_names[name] = []
                    if content[i-1][:1].isdigit():
                        info = content[i-1].split(":")
                        station = Station(info[0],info[1])
                        self.station_names[name].append(station)
                    if content[i+1][:1].isdigit():
                        info = content[i+1].split(":")
                        station = Station(info[0],info[1])
                        self.station_names[name].append(station)

    def find_start_and_end(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[i].stations)):
                if (self.head_hue in self.map[i].name
                   and self.map[i].stations[j].id == self.head_pos):
                    self.start = self.map[i].stations[j]
                if (self.tail_hue in self.map[i].name
                   and self.map[i].stations[j].id == self.tail_pos):
                    self.end = self.map[i].stations[j]

    def bfs(self):
        routes = []
        queue = collections.deque([[self.start]])
        seen = set()
        seen.add(self.start.name)
        while queue:
            path = queue.popleft()
            if path[-1].name == self.end.name:
                try:
                    seen.remove(self.end.name)
                except KeyError:
                    pass
                routes.append(path)
                continue
            for nearby in self.station_names[path[-1].name]:
                if nearby.name not in seen:
                    queue.append(path + [nearby])
                    seen.add(nearby.name)
        return routes


def main():
    m = Map('file')
    routes = m.bfs()
    for i, route in enumerate(routes):
        print("Route " + str(i+1) + ":")
        print("\033[1;30m => \033[0;0m".join(station.name for station in route))


if __name__ == '__main__':
    main()
