import threading
import queue
import requests
import pathlib


def check_proxies():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get('https://ipinfo.io/json',
                               proxies={'http': proxy,
                                        'https': proxy})
        except:
            continue
        if res.status_code == 200:
            print(proxy)



if __name__=="__main__":

    q = queue.Queue()
    valid_proxies = []
    print(pathlib.Path.cwd())
    with open('C:\\code\\reckless_web\\reckless\\horsemen\\data_collection\\proxies\\proxy_list.txt', 'r') as f:
        proxies = f.read().split('\n')
        for p in proxies:
            q.put(p)

    for _ in range(10):
        threading.Thread(target=check_proxies).start()



