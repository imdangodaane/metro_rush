#!/usr/bin/env python3
import collections
import time


class Station:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.neighbor = []

    def add_neighbor(self, n_info):
        self.neighbor.append(n_info)


class Line:
    def __init__(self, name):
        self.name = name
        self.line = list()

    def append_city(self, city):
        self.line.append(city)


class Map:
    def __init__(self):
        self.map = list()

    def append_line(self, line):
        self.map.append(line)


def read_file():
    f = open('file','r')
    content = f.readlines()
    content = [e.strip() for e in content]
    return content


def create_map():
    m = Map()
    content = read_file()
    for i in content:
        if i.startswith('#'):
            # try:
            #     m.append_line(train)
            # except:
            #     pass
            train = Line(i[1:])
        elif i[:1].isdigit():
            if ":Conn:" not in i:
                id, name = i.split(":", 1)
                station = Station(id,name.strip())
                train.line.append(station)
            else:
                id, name, _, _= i.split(":")
                station = Station(id,name.strip())
                train.line.append(station)
            m.append_line(train)
        elif "=" in i:
            if "START" in i:
                line_start, position = i.split()
                _, color_start = line_start.split("=")
                _, position_start = position.split(":")
            elif  "END" in i:
                line_end, position = i.split()
                _, color_end = line_end.split("=")
                _, position_end = position.split(":")
            else:
                _, leng_trains = i.split("=")
    return m, color_start, position_start, color_end, position_end


def find_neighbor():
    content = read_file()
    station_names = {}
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
                    station_names[name].append(station)
                if content[i+1][:1].isdigit():
                    info = content[i+1].split(":")
                    station = Station(info[0],info[1])
                    station_names[name].append(station)
            except IndexError:
                continue
            except KeyError:
                station_names[name] = []
                if content[i-1][:1].isdigit():
                    info = content[i-1].split(":")
                    station = Station(info[0],info[1])
                    station_names[name].append(station)
                if content[i+1][:1].isdigit():
                    info = content[i+1].split(":")
                    station = Station(info[0],info[1])
                    station_names[name].append(station)
    return station_names


def find_start_and():
    m, color_start, position_start, color_end, position_end = create_map()
    for i in range(len(m.map)):
        for j in range(len(m.map[i].line)):
            if color_start in m.map[i].name and m.map[i].line[j].id == position_start:
                start = m.map[i].line[j]
            if color_end in m.map[i].name and m.map[i].line[j].id == position_end:
                end = m.map[i].line[j]
    return start, end


def bfs():
    tmp = []
    m, color_start, position_end, color_end, position_end = create_map()
    start, end = find_start_and()
    station_names = find_neighbor()
    queue = collections.deque([[start]])
    seen = set()
    seen.add(start.name)
    while queue:
        path = queue.popleft()
        x = path[-1]
        if x.name == end.name:
            tmp.append(path)
            try:
                seen.remove(end.name)
            except KeyError:
                pass
            continue
        for nearby in station_names[x.name]:
            if nearby.name not in seen:
                queue.append(path + [nearby])
                seen.add(nearby.name)
    return tmp


def main():
    routes = bfs()
    for i, route in enumerate(routes):
        print("Route " + str(i+1) + ":")
        print("\033[1;30m => \033[0;0m".join(station.name for station in route))


if __name__ == '__main__':
    main()
