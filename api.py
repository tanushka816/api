from json import JSONDecoder
import requests
import re
from datetime import datetime
import sys


LAST_EARLY_STAT_DATE = re.compile("\d{2}\.\d{2}\.\d{4}")
MUST_HAVE = "http://api.github.com"
# WORKERS = ["kek", "mogmi", "getify", "bitinn", "hsoft", "lxc", "marcan"]
# WORKERS = ["kek", "mogmi", "getify"]
WORKERS = ["bitinn", "hsoft", "lxc", "marcan"]
workers_stat = {}


def get_count_stars_followers(user):
    global MUST_HAVE
    result = {"s": 0, "f": 0}
    answer_f = requests.get(MUST_HAVE + f"/users/{user}")  # for followers
    answer_st = requests.get(MUST_HAVE + f"/users/{user}/repos")  # for stars
    if answer_f.status_code != 200 or answer_st.status_code != 200:
        err = answer_f.status_code if answer_f.status_code != 200  else answer_st.status_code
        print(f"Program got an error {err}.\nPlease, repeat later.")
        sys.exit(1)

    info = JSONDecoder().decode(answer_f.text)
    result["f"] = info["followers"]
    info = JSONDecoder().decode(answer_st.text)
    for note in info:
        result["s"] += note["stargazers_count"]

    def count_scope(stat):
        scope = stat["s"]*3 + stat["f"]*7
        workers_stat[user] = scope

    count_scope(result)


def get_early_one(file):
    result = {}
    with open(file, mode='r', encoding='utf-8') as f:
        early_stat = f.read().replace(' ', '')

    dates = LAST_EARLY_STAT_DATE.findall(early_stat)
    valid_workers_info = early_stat.split(dates[-1])[1].strip().split('\n')
    for worker_stat in valid_workers_info:
        worker_stat = worker_stat.strip().split(':')
        result[worker_stat[0]] = int(worker_stat[1])
    return result


def save_stat(file):
    year, month, day = str(datetime.now().date()).split('-')
    with open(file, mode='a') as f:
        f.write(day + '.' + month + '.' + year + '\n')
        for worker in workers_stat.keys():
            f.write(worker + ' : ' + str(workers_stat[worker]) + '\n')
        f.write('\n')

if __name__ == "__main__":
    for everybody in WORKERS:
        get_count_stars_followers(everybody)

    early_stat = get_early_one("stat.txt")
    for name in early_stat:
        if workers_stat[name] > early_stat[name]:
            print(f"{name} works good this time")
        if workers_stat[name] == early_stat[name]:
            print(f"{name} can be work better!")
        if workers_stat[name] < early_stat[name]:
            print(f"{name} should work better!!!")

    save_stat("stat.txt")
