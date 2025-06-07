import string
import random
from names import get_first_name
from random_username.generate import generate_username

used_logins = []
team_names_file = open('assets/team_names.txt', 'r')

org_ids = [i for i in range(6, 106)]
captain_ids = [i for i in range(106, 306)]
team_ids = [i for i in range(1, 201)]
part_ids = [i for i in range(306, 1106)]

hack_names_file = open('assets/hack_names.txt')
hack_themes_file = open('assets/hack_themes.txt')
hack_addresses_file = open('assets/addresses.txt')
hack_dates_file = open('assets/dates.txt')

cap_team_relation = []
random.shuffle(captain_ids)
random.shuffle(org_ids)


def get_password(length):
    s1 = list(string.ascii_lowercase)
    s2 = list(string.ascii_uppercase)
    s3 = list(string.digits)

    random.shuffle(s1)
    random.shuffle(s2)
    random.shuffle(s3)

    part1 = round(length * (30 / 100))
    part2 = round(length * (20 / 100))

    result = []

    for x in range(part1):
        result.append(s1[x])
        result.append(s2[x])

    for x in range(part2):
        result.append(s3[x])

    random.shuffle(result)

    password = "".join(result)
    return password


class UserTesting:
    def __init__(self):
        self.name = get_first_name()
        self.login = generate_username()[0]
        self.rating = random.randint(1, 10000)


class User:
    def __init__(self):
        self.name = get_first_name()
        self.password = get_password(random.randint(8, 25))
        self.login = generate_username()[0]

    def change_login(self):
        self.login = generate_username()[0]


class Admin(User):
    def __init__(self):
        self.role = 1
        super().__init__()


class Organizer(User):
    def __init__(self):
        self.role = 2
        super().__init__()


class Captain(User):
    def __init__(self):
        self.role = 3
        self.rating = random.randint(10, 100)
        super().__init__()


class Participant(User):
    def __init__(self):
        self.role = 4
        self.rating = random.randint(10, 100)
        self.team_id = 0
        super().__init__()


class Team:
    def __init__(self):
        self.name = team_names_file.readline().split("\n")[0]
        self.n_participants = 5
        self.rating = 0
        self.captain_id = captain_ids.pop()


class Hackathon:
    def __init__(self, _id):
        self.id = _id
        self.name = hack_names_file.readline().split('\n')[0]
        self.theme = hack_themes_file.readline().split('\n')[0]
        self.address = hack_addresses_file.readline().split('\n')[0]
        self.date = hack_dates_file.readline().split('\n')[0]
        self.duration = random.randint(12, 73)
        self.n_members = random.randint(3, 20)

        self.org_id = org_ids.pop()


def toCsvStr(item_list):
    res = ''
    for i in range(len(item_list) - 1):
        res += str(item_list[i]) + ';'

    res += str(item_list[-1]) + "\n"

    return res


def generate_users_type(n: int, filename: string, role: int):
    file = open(filename, 'w', newline='')
    for i in range(0, n):

        if role == 1:
            user = Admin()
        elif role == 2:
            user = Organizer()
        elif role == 3:
            user = Captain()
        else:
            user = Participant()

        while user.login in used_logins:
            user.change_login()

        csvstr = toCsvStr([user.name, user.login, user.password, str(user.role)])
        used_logins.append(user.login)
        file.write(csvstr)


def generate_teams(n: int, filename: string):
    file = open(filename, 'w')

    for i in range(0, n):
        team = Team()
        csvstr = toCsvStr([team.name, team.n_participants, team.captain_id, team.rating])
        file.write(csvstr)
        cap_team_relation.append([i + 1, team.captain_id])


def generate_t_p_list(team_id_list, part_id_list, filename):
    file = open(filename, 'w')
    i = 0
    random.shuffle(team_id_list)
    for j in range(0, len(part_id_list)):
        csvstr = toCsvStr([part_id_list[j], team_id_list[i]])
        file.write(csvstr)

        if (j + 1) % 4 == 0 and j != 0:
            print(i, j, len(part_id_list))
            csvstr = toCsvStr([cap_team_relation[i][1], cap_team_relation[i][0]])
            file.write(csvstr)
            i += 1


def generate_hackathons(n: int, filename: str, h_t_relation_filename, _team_ids):
    file = open(filename, 'w')
    relation_file = open(h_t_relation_filename, 'w')

    hack_list = []

    for i in range(0, n):  # генерим хакатоны
        hack = Hackathon(i + 1)
        hack_list.append(hack)

    for hack in hack_list:  # генерим какие команды участвуют в каких хакатонах
        hack_team_list = random.sample(_team_ids, hack.n_members)

        for team_id in hack_team_list:  # cразу пишем в файл
            csvstr = toCsvStr([team_id, hack.id])
            relation_file.write(csvstr)

        three = random.sample(hack_team_list, 3)  # из участников выбираем 3-х победителей
        hack.first_id, hack.second_id, hack.third_id = three[0], three[1], three[2]

        csvstr = toCsvStr([hack.name, hack.address, hack.date, hack.theme, hack.duration, hack.n_members, hack.org_id,
                           hack.first_id, hack.second_id, hack.third_id])
        file.write(csvstr)

    file.close()


def generate_ratings(res_filename):
    file = open(res_filename, 'w')

    for i in range(min(captain_ids), max(part_ids)):
        csvstr = toCsvStr([i, random.randint(0, 15)])
        file.write(csvstr)


def generate_users(n, res_filename):
    file = open(res_filename, 'w')

    for i in range(n):
        user = UserTesting()
        csvstr = toCsvStr([user.name, user.login, user.rating])
        file.write(csvstr)

    file.close()


data_location = 'generated_data/'
#
# generate_users_type(5, data_location + 'admins.csv', 1)
# generate_users_type(100, data_location + "organizers.csv", 2)
# generate_users_type(200, data_location + "captains.csv", 3)
# generate_teams(200, data_location + "teams.csv")
# generate_users_type(800, data_location + "participants.csv", 4)
# generate_t_p_list(team_ids, part_ids, data_location + "t_p_list.csv")
# generate_hackathons(100, data_location + "hackathons.csv", data_location + 'h_t_list.csv', team_ids)

generate_ratings(data_location + "ratings.csv")

# для иссл. части
# generate_users(10000, data_location + "users_testing10000.csv")
# generate_users(25000, data_location + "users_testing25000.csv")
# generate_users(50000, data_location + "users_testing50000.csv")
# generate_users(100000, data_location + "users_testing100000.csv")
# generate_users(150000, data_location + "users_testing150000.csv")
# generate_users(200000, data_location + "users_testing200000.csv")
# generate_users(250000, data_location + "users_testing250000.csv")
# generate_users(300000, data_location + "users_testing300000.csv")
# generate_users(350000, data_location + "users_testing350000.csv")
# generate_users(400000, data_location + "users_testing400000.csv")
# generate_users(450000, data_location + "users_testing450000.csv")
# generate_users(500000, data_location + "users_testing500000.csv")
# generate_users(600000, data_location + "users_testing600000.csv")
# generate_users(700000, data_location + "users_testing700000.csv")
# generate_users(800000, data_location + "users_testing800000.csv")
# generate_users(900000, data_location + "users_testing900000.csv")
# generate_users(1000000, data_location + "users_testing1000000.csv")
