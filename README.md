# nginx_log_parser
tool for parsing nginx log

1. run database
```
sudo docker-compose up -d
```
2. compile tool
```
go build -o parser parser.go
```
3. run tool
```
./parser -buffer 10000 -db="tcp://127.0.0.1:9000?username=&debug=false" -workers 5 -input example_logs/example.log
```
or 
```
find example_logs/ -type f -name "*.log" -exec cat {} \; | ./parser -buffer 100000 -db="tcp://127.0.0.1:9000?username=&debug=false" -workers 8
```
4. wait
5. now you can connect to the database and make queries
```
$ sudo docker run --rm -it --net host yandex/clickhouse-server:latest clickhouse-client --host 127.0.0.1 --port 9000
ClickHouse client version 20.3.8.53 (official build).
Connecting to 127.0.0.1:9000 as user default.
Connected to ClickHouse server version 20.3.8 revision 54433.

localhost :) SELECT domain,COUNT() FROM requests WHERE timestamp > '2020-05-18 09:21:08' AND url_path='/index.html' GROUP BY domain ORDER BY domain;

SELECT 
    domain, 
    COUNT()
FROM requests
WHERE (timestamp > '2020-05-18 09:21:08') AND (url_path = '/index.html')
GROUP BY domain
ORDER BY domain ASC

┌─domain──────────────┬─COUNT()─┐
│ domain1.example.com │  325850 │
│ domain2.example.com │  325678 │
│ domain3.example.com │  325267 │
└─────────────────────┴─────────┘

3 rows in set. Elapsed: 0.196 sec. Processed 10.00 million rows, 585.20 MB (50.98 million rows/s., 2.98 GB/s.) 

localhost :) 

```
