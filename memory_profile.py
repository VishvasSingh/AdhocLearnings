from memory_profiler import profile
# import tracemalloc


"""
Profile decorator prints this for the function: 


Line #    Mem usage    Increment  Occurrences   Line Contents
=============================================================
     4     27.2 MiB     27.2 MiB           1   @profile
     5                                         def calculate_squares_upto(n: int):
     6                                             # snapshot2 = tracemalloc.take_snapshot()
     7    412.0 MiB    384.8 MiB    10000001       squares = [n*n for n in range(n)]
     8                                             # snapshot3 = tracemalloc.take_snapshot()
     9                                             # return snapshot2, snapshot3



"""




@profile
def calculate_squares_upto(n: int):
    # snapshot2 = tracemalloc.take_snapshot()
    squares = [n*n for n in range(n)]
    # snapshot3 = tracemalloc.take_snapshot()
    # return snapshot2, snapshot3



if __name__ == '__main__':
    # tracemalloc.start()
    # snapshot1 = tracemalloc.take_snapshot()
    calculate_squares_upto(10000000)
    # topstats_1 = snapshot2.compare_to(snapshot1, 'lineno')
    # topstats_2 = snapshot3.compare_to(snapshot2, 'lineno')
    # topstats_3 = snapshot3.compare_to(snapshot1, 'lineno')

    # print("[ Top 3 biggest memory hogs between snap 1 and 2]")
    # for stat in topstats_1[:3]:
    #     print(stat)
    #
    # print(f"\n {'--' * 15} \n ")
    #
    # print("[ Top 3 biggest memory hogs between snap 3 and 2]")
    # for stat in topstats_2[:3]:
    #     print(stat)
    #
    # print(f"\n {'--' * 15} \n ")
    #
    # print("[ Top 3 biggest memory hogs between snap 3 and 1]")
    # for stat in topstats_3:
    #     print(stat)
    #
    # print(f"\n {'--' * 15} \n ")


