import threading
import requests
import argparse
import time

request_counter = 0
printed_msgs = set()
lock = threading.Lock()

def print_msg(msg):
    global request_counter
    with lock:
        if msg not in printed_msgs:
            print(f"\n{msg} after {request_counter} requests")
            printed_msgs.add(msg)

def handle_status_codes(status_code):
    global request_counter
    with lock:
        request_counter += 1
        print(f"\r{request_counter} requests sent", end="", flush=True)

    if status_code == 429:
        print_msg("You have been throttled")
    elif status_code == 500:
        print_msg("Status code 500 received")

def send_get(url):
    try:
        resp = requests.get(url)
        handle_status_codes(resp.status_code)
    except Exception:
        pass

def send_post(url, data):
    try:
        resp = requests.post(url, data=data)
        handle_status_codes(resp.status_code)
    except Exception:
        pass

def worker(url, data=None):
    if data:
        send_post(url, data)
    else:
        send_get(url)
        
def send_get(url):
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")  # 👈 Add this
        handle_status_codes(resp.status_code)
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="HTTP stress tester")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--get", help="GET request URL")
    group.add_argument("-p", "--post", help="POST request URL")
    parser.add_argument("-d", "--data", help="Payload for POST")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of threads")

    args = parser.parse_args()
    url = args.get or args.post
    data = args.data
    thread_count = args.threads

    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=worker, args=(url, data))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    print("\nDone.")

if __name__ == "__main__":
    main()
