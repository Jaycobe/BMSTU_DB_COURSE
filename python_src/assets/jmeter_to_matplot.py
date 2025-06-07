import pandas as pd
from matplotlib import pyplot as plt


# n - число запросов в пользовательском сценарии
# breakpoint - число пользователей, на котором надо остановить обработку, по умолчанию - 0 (не останавливать)
#
def file_to_plot(input_name, output_name, n, breakpoint=0):
    data = pd.read_csv(input_name, usecols=['elapsed', 'label', 'allThreads'])

    x = []  # число потоков
    y = []  # среднее время ответа

    break_flag = False if breakpoint == 0 else True

    num = 0  # общее время обработки для конкретного числа потоков
    denom = 0  # число потоков

    for i in range(0, data.shape[0]):
        num += data['elapsed'][i]
        denom += 1

        if data['allThreads'][i] not in x:

            if break_flag and data['allThreads'][i] == breakpoint:
                break

            x.append(data['allThreads'][i])

            if denom != 0:
                y.append((num/(denom/n))/100)
                denom = 0

    plt.figure(figsize=(8, 6))
    plt.plot(x, y)
    plt.subplots_adjust(left=0.1, right=0.99, top=0.99, bottom=0.1)
    # plt.yticks([i for i in range(0, 13000, 1000)])
    # plt.scatter(x, y, s=3)
    plt.xlabel('Число пользователей')
    plt.ylabel('Среднее время ответа, мс')
    plt.grid()
    plt.savefig(output_name)
    plt.show()


file_to_plot('test_results.csv', 'exp1_100.png', 3, 100)
file_to_plot('test_results.csv', 'exp1_400.png', 3, 400)

file_to_plot('test_results2.csv', 'exp2_100.png', 3, 100)
file_to_plot('test_results2.csv', 'exp2_400.png', 3, 400)

file_to_plot('test_results3.csv', 'exp3_100.png', 3, 100)
file_to_plot('test_results3.csv', 'exp3_400.png', 3, 400)
