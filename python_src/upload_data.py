import psycopg2

open_files = []


def get_insert_user_query(args):
    name = args[0]
    login = args[1]
    password = args[2]
    role = args[3]

    query = f"insert into Users values (default, '{name}', '{login}', '{password}', {role})"

    return query


def get_insert_team_query(args):
    name = args[0]
    n_members = args[1]
    cap_id = args[2]
    rating = args[3]

    query = f"insert into Teams values (default, '{name}', '{n_members}', '{rating}', {cap_id})"

    return query


def get_insert_t_p_query(args):
    part_id = args[0]
    team_id = args[1]

    query = f"insert into t_p_list values ('{team_id}', '{part_id}')"
    return query


def get_insert_t_h_query(args):
    team_id = args[0]
    hack_id = args[1]

    query = f"insert into h_t_list values ('{hack_id}', '{team_id}')"

    return query


def get_insert_hackathon_query(args):
    name = args[0]
    address = args[1]
    date = args[2]
    theme = args[3]
    duration = args[4]
    org_id = args[5]
    first_id, second_id, third_id = args[6], args[7], args[8]

    query = f"insert into hackathons values (default, '{name}', '{address}', '{date}', '{theme}', '{duration}', '{org_id}'," \
            f"'{first_id}', '{second_id}','{third_id}')"

    return query


def get_insert_rating_query(args):
    id = args[0]
    rating = args[1]

    query = f"insert into ratings values({id}, {rating})"

    return query


connection = psycopg2.connect(user='postgres',
                              password='postgres',
                              port=228,
                              host='localhost')

cur = connection.cursor()

filenames = ['admins.csv', 'organizers.csv', 'captains.csv', 'participants.csv', 'teams.csv', 't_p_list.csv',
             'hackathons.csv', "h_t_list.csv", "ratings.csv"]
files = []

for f in filenames:
    files.append(open('generated_data/' + f))

for i in range(0, 9):
    for line in files[i]:
        args = line.split(';')

        if i < 4:
            query = get_insert_user_query(args)
        elif i == 4:
            query = get_insert_team_query(args)
        elif i == 5:
            query = get_insert_t_p_query(args)
        elif i == 6:
            query = get_insert_hackathon_query(args)
        elif i == 7:
            query = get_insert_t_h_query(args)
        elif i == 8:
            query = get_insert_rating_query(args)

        cur.execute(query)
        connection.commit()

# test users
# cur.execute("insert into users values (default, 'SuperAdmin', 'admin', 'admin', 1)")
# cur.execute("insert into users values (default, 'Test Organizer', 'organizer', 'organizer', 2);")
# cur.execute("insert into users values (default, 'Test Captain', 'captain', 'captain', 3);")
# cur.execute("insert into users values (default, 'Test Participant 1', 'participant1', 'participant1', 4);")
# cur.execute("insert into users values (default, 'Test Participant 2', 'participant2', 'participant2', 4);")
# cur.execute("insert into users values (default, 'Test Participant 3', 'participant3', 'participant3', 4);")
# cur.execute("insert into users values (default, 'Test Participant 4', 'participant4', 'participant4', 4);")
# cur.execute("insert into users values (default, 'Test Participant 5', 'participant5', 'participant5', 4);")

for file in files:
    file.close()

cur.close()
connection.close()
