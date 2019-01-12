#!/usr/bin/env python3
import collections
from sys import stderr
import time


class Station:
    def __init__(self, id, name, line):
        self.id = id
        self.name = name
        self.neighbor = []
        self.line = line
        self.trains = collections.deque()

    def add_neighbor(self, neighbor_info):
        self.neighbor.append(neighbor_info)

    def add_train(self, id, train):
        self.trains.append((id, train))

    def remove_train(self, id, train):
        self.trains.remove((id, train))


class Line:
    def __init__(self, name):
        self.name = name
        self.stations = []


class Train:
    def __init__(self, id, current_station, current_line):
        self.id = id
        self.name = "T" + str(id)
        self.route = None
        self.current_station = current_station
        self.current_line = current_line

    def move_to(self, next_station):
        self.current_station = next_station

    def change_line(self, next_line):
        self.current_line = next_line


class Map:
    def __init__(self, file_name):
        self.routes = []
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
        self.trains = []
        self.transfer_points = set()

        content = self.read_file(self.file_name)
        self.create_map(content)
        self.find_neighbor(content)
        self.find_start_and_end()
        self.metro_add_trains()

    def metro_add_trains(self):
        for i in range(int(self.total_trains)):
            train = Train(i+1, self.start, self.start.line)
            self.trains.append((i+1, train))
            self.start.add_train(i+1, train)

    def print_status(self, route):
        for station in route:
            print(station.name)
            for id, train in station.trains:
                print(train.name, end=" ")
            print()

    def metro_run_train(self):
        turn = 0
        route = self.routes[0]
        home = set()

        route_name = [i.name for i in route]
        tmp = " => ".join(route_name)
        while len(route[-1].trains) != int(self.total_trains):
            print("Turn: " + str(turn) + " Route: (" + tmp + ")")
            self.print_status(route)
            for id, train in self.trains:
                if id in home:
                    continue
                current_pos = route.index(train.current_station)
                if route[current_pos] == route[-1]:
                    home.add(id)
                    continue
                next_station = route[current_pos + 1]
                if train.current_station.name in self.transfer_points:
                    if next_station.line != train.current_line:
                        train.change_line(next_station.line)
                        continue
                if next_station == route[-1] or len(next_station.trains) == 0:
                    train.move_to(next_station)
                    next_station.add_train(id, train)
                    route[current_pos].remove_train(id, train)
            turn += 1
            time.sleep(0.1)
        print("Turn: " + str(turn) + " Route: (" + tmp + ")")
        self.print_status(route)
        print("===========================================")
        print()
        print("Total turn = " + str(turn))

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
        for i in content:
            if i.startswith('#'):
                line = Line(i[1:])
                self.append_line(line)
            elif i[:1].isdigit():
                if ":Conn:" not in i:
                    id_name = i.split(":")
                    station = Station(id_name[0], id_name[1].strip(), line.name)
                    line.stations.append(station)
                else:
                    id_name = i.split(":")
                    station = Station(id_name[0], id_name[1].strip(), line.name)
                    line.stations.append(station)
                    self.transfer_points.add(station.name)
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
            if content[i].startswith('#'):
                line = Line(content[i][1:])
            if content[i][:1].isdigit():
                info = content[i].split(":")
                if len(info) == 2:
                    id, name = info[0], info[1]
                elif len(info) == 4:
                    id, name, _, connect = info[0], info[1], info[2], info[3]
                try:
                    if content[i-1][:1].isdigit():
                        info = content[i-1].split(":")
                        station = Station(info[0],info[1],line.name)
                        self.station_names[name].append(station)
                    if content[i+1][:1].isdigit():
                        info = content[i+1].split(":")
                        station = Station(info[0],info[1],line.name)
                        self.station_names[name].append(station)
                except IndexError:
                    continue
                except KeyError:
                    self.station_names[name] = []
                    if content[i-1][:1].isdigit():
                        info = content[i-1].split(":")
                        station = Station(info[0],info[1],line.name)
                        self.station_names[name].append(station)
                    if content[i+1][:1].isdigit():
                        info = content[i+1].split(":")
                        station = Station(info[0],info[1],line.name)
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

    def find_route_bfs(self):
        self.routes = []
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
                self.routes.append(path)
                continue
            for nearby in self.station_names[path[-1].name]:
                if nearby.name not in seen:
                    queue.append(path + [nearby])
                    seen.add(nearby.name)
        return self.routes

    def print_routes(self):
        routes = self.routes
        for i, route in enumerate(routes):
            print("Route " + str(i+1) + ":")
            print("\033[1;30m => \033[0;0m".join(station.name for station in route))

    def bfs(self):
        self.find_route_bfs()


def main():
    m = Map('delhi-metro-stations')
    m.bfs()
    m.metro_run_train()
    # for line in m.map:
        # print("\033[4;31m" + line.name + ":" + "\033[0m")
        # for station in line.stations:
        #     print(station.name)


if __name__ == '__main__':
    main()
