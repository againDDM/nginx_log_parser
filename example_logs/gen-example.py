#!/usr/bin/env python3
import random
from datetime import datetime, timedelta, tzinfo


class fake_domain(object):
    __slots__ = ['value',]

    def __init__(self):
        self.value = f"domain{random.randint(1, 3)}.example.com"

    def __str__(self):
        return self.value

class fake_user_agent(object):
    __slots__ = ['value',]
    choises = [
        "Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 7.1.1; G8231 Build/41.2.A.0.219; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-en) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/74.0.3729.157 Safari/537.36",
        "Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebkit/538.1 (KHTML, like Gecko) SamsungBrowser/1.1 TV Safari/538.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; 125LA; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
        "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763",
    ]

    def __init__(self):
        self.value = fake_user_agent.choises[random.randint(0, len(fake_user_agent.choises) - 1)]

    def __str__(self):
        return self.value


class fake_method(object):
    choises = ["GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "GET", "POST", "POST", "POST", "OPTIONS", "POST", "PUT", "DELETE", "PUT", "DELETE", "PUT", "DELETE", "PUT", "DELETE", "PATCH"]
    __slots__ = ['value',]

    def __init__(self):
        self.value = fake_method.choises[random.randint(0, len(fake_method.choises) - 1)]

    def __str__(self):
        return self.value


class fake_url(object):
    __slots__ = ['value',]
    api_objects = ["moon", "earth", "sun", "mars", "venera", "uran", "user"]
    names = ["first", "second", "dog", "cat", "sometext", "notempty"]
    per_page = [5, 10, 20, 50, 100]

    def __init__(self, method):
        if method == "GET" and not random.randint(0, 5):
            self.value = "/index.html"
            return
        aobj = fake_url.api_objects[random.randint(0, len(fake_url.api_objects) - 1)]
        self.value = f"/api/v{random.randint(1, 3)}/{aobj}"
        oid = random.randint(11, 99)
        if method in ["PUT", "DELETE", "PATCH"]:
            self.value = f"{self.value}/{oid}"
        if method == "GET" and aobj != "user":
            if random.randint(0, 2):
                self.value = f"{self.value}/{oid}"
            else:
                self.value += f"?pagesize={fake_url.per_page[random.randint(0, len(fake_url.per_page) - 1)]}"
                if random.randint(0, 2):
                    self.value += f"&filter={fake_url.names[random.randint(0, len(fake_url.names) - 1)]}"
                page = random.randint(1, 5)
                if page > 1:
                    self.value +=f"&page={page}"

    def __str__(self):
        return self.value


class fake_date(object):
    last = datetime.now()
    __slots__ = ['value',]

    def __init__(self):
        fake_date.last += timedelta(milliseconds=random.randint(0, 16384))
        self.value = fake_date.last

    def __str__(self):
        return self.value.strftime('%d/%b/%Y:%H:%M:%S +0000')


class fake_ip(object):
    __slots__ = ['value',]
    def __init__(self):
        self.value = ".".join(str(random.randint(0, 255)) for i in range(4))

    def __str__(self):
        return self.value


def rand_code(method):
    if not random.randint(0, 100):
        return 500
    if not random.randint(0, 100):
        return 401
    if method == "POST":
        return 201
    if method == "DELETE":
        return 204
    return 200

def rand_reffer(method):
    if method != "GET":
        return f'{fake_domain()}{fake_url("GET")}'
    if random.randint(0, 2):
        return f'{fake_domain()}{fake_url("GET")}'
    return "-"


def main():
    for _ in range(10000000):
        method = str(fake_method())
        print(f'[{fake_date()}] {fake_domain()} "{method} {fake_url(method)} HTTP/1.1" from: {fake_ip()} port: {random.randint(21048, 41048)} user: {random.randint(11, 99)} to: - {rand_code(method)} {random.randint(101, 99999)} "{rand_reffer(method)}" "{fake_user_agent()}" "-"')


if __name__ == "__main__":
    main()