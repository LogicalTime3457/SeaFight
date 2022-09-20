from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # сравненение координат разных точек
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # выводит наши коорд., потом их можно помещать в список
    # д/дальнейшей проверки на совпадения
    def __repr__(self):
        return f"({self.x}, {self.y})"

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "You try shoot over the board's edge!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "You have shot in this dot already!"


class BoardWrongShipException(BoardException):
    pass

# определяем класс корабля с началом корабля, его длинной
# и вектором(горизональный или вертикальный
class Ship:
    def __init__(self, bow, len_, vector):
        self.bow = bow
        self.len_ = len_
        self.vector = vector
        self.lives = len_

    @property # не просто метод, а свойство класса
    def dots(self):
        ship_dots = []
        for i in range(self.len_):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.vector == 0: # горизонтальый
                cur_x += i

            elif self.vector == 1: # вертикальный
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    # вот для этого и нужен метод __eq__
    def shooten(self, shot):
        return shot in self.dots


# класс Доска с видимостью и размером
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = [] # для хранения занятых точек
        self.ships = [] # для хранения списка кораблей

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)


    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Ship was destroyed!")
                    return False
                else:
                    print("Ship was wounded!")
                    return True
        self.field[d.x][d.y] = "."
        print("Failure!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    # в метод ask ничего не добавляем, говорит о том,
    # что он д.б. у потомков класса
    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"It is AI's step: {d.x + 1} {d.y + 1} ")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Your step: ").split()
            if len(cords) != 2:
                print("Input two coordinates!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Input integers!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # т.к. нумерация у поль-ля идет с 1


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("----------------")
        print("    Welcome     ")
        print("  to the game   ")
        print("   SEA  FIGHT   ")
        print("----------------")
        print("Input's format: x y")
        print("x - number of string")
        print("y - number of column")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Usre's board:")
            print(self.us.board)
            print("-" * 20)
            print("AI's board")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("User's step!")
                repeat = self.us.move()
            else:
                print("AI's step!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print("-" * 20)
                print("User is winner!")

            if self.us.board.defeat():
                print("-" * 20)
                print("AI is winner!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


b = Game()
b.start()

