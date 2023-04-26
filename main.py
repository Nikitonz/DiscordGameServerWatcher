import argparse
from datetime import datetime, timedelta, date
import requests

webhook_urls = [
    
]
picture_url = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/977e8c4f-1c99-46cd-b070-10cd97086c08/d36qrs5-017c3744-8c94-4d47-9633-d85b991bf2f7.png/v1/fill/w_512,h_512,q_80,strp/minecraft_hd_icon___mac___pc_by_hunterkharon_d36qrs5-fullview.jpg'
language = 'ru_ru'
gamename = 'Minecraft'


def getIP():
    response = requests.get("https://httpbin.org/ip")
    data = response.json()
    ip = data["origin"]
    return ip


def start():
    global time_launched
    print("started")
    time_launched = datetime.now().time()
    ip = getIP()

    data = {
        "username": f"{gamename} Server alert",
        "avatar_url": picture_url,
        "embeds": [
            {
                "title": "Server desc",
                "description": f"\nСервер запущен!\nIP: {ip}, Port: 25565\n```{ip}:25565```\nВремя запуска: {time_launched.strftime('%H:%M:%S')}",
                "color": 0x00FF00
            }
        ]
    }
    for url in webhook_urls:
        requests.post(url, json=data)
    with open("time.txt", 'w') as inp:
        inp.write(str(time_launched))


def stop():
    with open("time.txt", 'r') as gettime:
        time_launched = datetime.strptime(gettime.readline(), '%H:%M:%S.%f').time()
    print("finishing...")

    time_stopped = datetime.now().time()
    seconds_elapsed = (datetime.combine(date.today(), time_stopped) - datetime.combine(date.today(),
                                                                                       time_launched)).total_seconds()

    data = {
        "username": f"{gamename} Server alert",
        "avatar_url": picture_url,
        "embeds": [
            {
                "title": "Server desc",
                "description": f"\nСервер был остановлен. Время остановки: {time_stopped.strftime('%H:%M:%S')}\nСервер проработал={timedelta(seconds=seconds_elapsed)}",
                "color": 0x8B0000
            }
        ]
    }
    for url in webhook_urls:
        requests.post(url, json=data)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to run')
    args = parser.parse_args()

    if args.command == 'start':
        start()
    elif args.command == 'stop':
        stop()
    else:
        print(f'Unknown command: {args.command}')
    exit()