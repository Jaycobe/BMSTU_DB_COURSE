import time
import psycopg2.extensions
import matplotlib.pyplot as plt
N_ITER = 20


def get_insert_user_testing_query(args):
    name = args[0]
    login = args[1]
    rating = args[2]

    query = f"insert into users_testing values (default, '{name}', '{login}', '{rating}')"

    return query


def run_select_queries(n_iter):
    total_time = 0
    for i in range(n_iter):
        start_time = time.time()
        cursor.execute("select * from users_testing where username = 'culturedToucan5'")

        count = 0
        for record in cursor:
            count += 1

        end_time = time.time()
        total_time += end_time - start_time

    return total_time


def run_insert_queries(n_queries):
    total_time = 0
    file = open('generated_data/users_testing500000 (copy).csv')

    # вставка 10к записей за раз
    query = "copy users_testing(name, username, rating) from '/generated_data/users_testing10000.csv' delimiter ';'"
    start_time = time.time()
    cursor.execute(query)
    connection.commit()
    end_time = time.time()

    return end_time - start_time

    # вставка n_queries по одной
    # for i in range(n_queries):
    #     args = file.readline().split(';')
    #     query = get_insert_user_testing_query(args)
    #
    #     start_time = time.time()
    #     cursor.execute(query)
    #     connection.commit()
    #     end_time = time.time()
    #
    #     total_time += (end_time - start_time)

    return total_time


connection = psycopg2.connect(
  database="postgres",
  user="postgres",
  password="postgres",
  host="localhost",
  port="228"
)

cursor = connection.cursor()

# массив нужен для создания названий файлов, для другого количества надо нагенерить данные в файл с другим названием
n_arr = ['10000', '25000', '50000', '100000', '150000', '200000', '250000', '300000', '350000', '400000', '450000',
         '500000', '600000', '700000', '800000', '900000', '1000000']

time_arr = []
indexed_time_arr = []
indexing_time_arr = []
insertion_time_arr = []
insertion_indexed_time_arr = []

cursor.execute("truncate table users_testing")
cursor.execute('drop index if exists user_index_1')

for n in n_arr:
    cursor.execute("copy users_testing(name, username, rating) from '/generated_data/users_testing" + n + ".csv' delimiter ';'")
    connection.commit()

    total_time = run_select_queries(N_ITER)

    print(n + " : " + str(total_time))
    time_arr.append(total_time)

    total_time = run_insert_queries(1000)
    print(n + " insertion 1000: " + str(total_time))
    insertion_time_arr.append(total_time)

    cursor.execute('truncate table users_testing')
    cursor.execute("copy users_testing(name, username, rating) from '/generated_data/users_testing" + n + ".csv' delimiter ';'")
    connection.commit()

    # замер времени индексирования
    start_time = time.time()
    cursor.execute("create index user_index_1 on users_testing (username)")
    connection.commit()
    end_time = time.time()
    indexing_time_arr.append(end_time - start_time)

    total_time = run_select_queries(N_ITER)
    print(n + " indexed: " + str(total_time))
    indexed_time_arr.append(total_time)

    total_time = run_insert_queries(1000)
    print(n + "indexed insertion 1000: " + str(total_time))
    insertion_indexed_time_arr.append(total_time)

    cursor.execute('truncate table users_testing')
    cursor.execute('drop index user_index_1')

y_axis = [int(i) for i in n_arr]

plt.figure(figsize=(8, 6))
plt.plot(y_axis, time_arr, label="Время выполнения без индексации")
plt.plot(y_axis, indexed_time_arr, linestyle='dashed', label="Время выполнения с индексацией")
plt.grid()
plt.subplots_adjust(left=0.1, right=0.99, top=0.99, bottom=0.1)
plt.ylabel("Время, с")
plt.xlabel('Число записей в БД')
plt.legend()
plt.savefig('assets/indexing_both.png')
plt.show()

plt.figure(figsize=(8, 6))
plt.plot(y_axis, indexed_time_arr)
plt.ylabel("Время, с")
plt.xlabel('Число записей в БД')
plt.grid()
plt.subplots_adjust(left=0.1, right=0.99, top=0.99, bottom=0.1)
plt.savefig('assets/indexing_separate.png')
plt.show()

plt.figure(figsize=(8, 6))
plt.plot(y_axis, indexing_time_arr)
plt.ylabel("Время, с")
plt.xlabel('Число записей в БД')
plt.grid()
plt.subplots_adjust(left=0.1, right=0.99, top=0.99, bottom=0.1)
plt.savefig('assets/indexing_time.png')
plt.show()

plt.figure(figsize=(8, 6))
plt.plot(y_axis, insertion_time_arr, label='Время вставки без индексации')
plt.plot(y_axis, insertion_indexed_time_arr, label='Время вставки с индексацией', linestyle='dashed')
plt.ylabel("Время, с")
plt.xlabel('Число записей в БД')
plt.grid()
plt.legend()
plt.savefig('assets/insertion_time.png')
plt.show()
