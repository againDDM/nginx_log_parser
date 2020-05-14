package main

import (
	"bufio"
	"database/sql"
	"flag"
	"log"
	"os"
	"regexp"
	"runtime"
	"strconv"
	"sync"
	"time"

	"github.com/ClickHouse/clickhouse-go"
)

type config struct {
	inputFile  string
	dbPath     string
	workers    int
	bufferSize int
}

func getConfig() (cfg config) {
	cfg.parse()
	return cfg
}

func (cfg *config) parse() {
	flag.StringVar(&cfg.inputFile, "input", "/dev/stdin", "input file path")
	flag.StringVar(&cfg.dbPath, "db", "tcp://127.0.0.1:9000?username=&debug=false", "input database string")
	flag.IntVar(&cfg.workers, "workers", runtime.NumCPU(), "number of parsers")
	flag.IntVar(&cfg.bufferSize, "buffer", 10000, "size of buffer in strings")
	flag.Parse()
}

type dbWorker struct {
	conection *sql.DB
	inChan    chan [][]interface{}
	buffSize  int
	wg        *sync.WaitGroup
}

func newDBWorker(dbPath string, qSize int) (dbw dbWorker) {
	dbw.inChan = make(chan [][]interface{}, qSize)
	dbw.initDB(dbPath)
	dbw.wg = &sync.WaitGroup{}
	return dbw
}

func (dbw *dbWorker) initDB(path string) {
	var err error
	dbw.conection, err = sql.Open("clickhouse", path)
	if err != nil {
		log.Fatalln(err)
	}
	if err := dbw.conection.Ping(); err != nil {
		if exception, ok := err.(*clickhouse.Exception); ok {
			log.Printf("[%d] %s \n%s\n", exception.Code, exception.Message, exception.StackTrace)
			log.Fatalln(err)
		} else {
			log.Fatalln(err)
		}
		return
	}
	dbw.conection.SetMaxOpenConns(1)
	_, err = dbw.conection.Exec(`CREATE TABLE IF NOT EXISTS requests (
	timestamp DATETIME,
	domain TEXT,
	request TEXT,
	url_path TEXT,
	from_full TEXT,
	from_ip_address TEXT,
	status_code INTEGER,
	user_agent TEXT) engine=Log`)
	if err != nil {
		log.Fatalln(err)
	}
}

func (dbw *dbWorker) serve() (chan [][]interface{}, *sync.WaitGroup) {
	dbw.wg.Add(1)
	go func(inc <-chan [][]interface{}, wg *sync.WaitGroup) {
		runtime.LockOSThread()
		defer dbw.conection.Close()
		for task := range inc {
			if len(task) == 0 {
				continue
			}
			executeMany(dbw.conection, task)
		}
		wg.Done()
	}(dbw.inChan, dbw.wg)
	return dbw.inChan, dbw.wg
}

func executeMany(dbc *sql.DB, task [][]interface{}) {
	tx, err := dbc.Begin()
	if err != nil {
		log.Println(err)
		return
	}
	defer tx.Commit()
	stmt, err := tx.Prepare(
		"INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
	if err != nil {
		log.Println(err)
		return
	}
	defer stmt.Close()
	for _, row := range task {
		_, err := stmt.Exec(row...)
		if err != nil {
			log.Println(err)
			continue
		}
	}
}

type parseWorker struct {
	re   *regexp.Regexp
	wg   *sync.WaitGroup
	inc  <-chan []string
	outc chan<- [][]interface{}
}

func (wkr *parseWorker) serve() {
	for pack := range wkr.inc {
		message := make([][]interface{}, 0, len(pack))
		for _, raw := range pack {
			match := wkr.re.FindStringSubmatch(raw)
			if len(match) < 9 {
				log.Println("NOT MATCHED: ", raw)
				continue
			}
			t, err := time.Parse(tform, match[1])
			if err != nil {
				log.Println("ERROR", err, "\nLINE: ", raw)
				continue
			}
			i, err := strconv.Atoi(match[7])
			if err != nil {
				log.Println("ERROR", err, "\nLINE: ", raw)
				continue
			}
			message = append(message,
				[]interface{}{
					t, match[2], match[3], match[4],
					match[5], match[6], i, match[8],
				},
			)
		}
		wkr.outc <- message
	}
	wkr.wg.Done()
}

type parsersPool struct {
	pool []parseWorker
	re   *regexp.Regexp
	wg   *sync.WaitGroup
	inc  chan []string
	outc chan<- [][]interface{}
}

func newParsersPool(number int, res string, outc chan [][]interface{}) parsersPool {
	pp := *new(parsersPool)
	pp.outc = outc
	pp.inc = make(chan []string, number*2)
	pp.wg = &sync.WaitGroup{}
	pp.re = regexp.MustCompile(res)
	pp.pool = make([]parseWorker, 0, number)
	for i := 0; i < number; i++ {
		pp.pool = append(pp.pool, parseWorker{pp.re, pp.wg, pp.inc, pp.outc})
	}
	return pp
}

func (pp *parsersPool) serve() {
	for _, wkr := range pp.pool {
		pp.wg.Add(1)
		go wkr.serve()
	}
}

func shred(cfg config, outc chan<- []string) {
	input, err := os.Open(cfg.inputFile)
	if err != nil {
		log.Fatalln(err)
	}
	defer input.Close()
	scanner := bufio.NewScanner(input)
	scanner.Split(bufio.ScanLines)
	done := false
READ:
	for {
		messageBuff := make([]string, 0, cfg.bufferSize)
	BUFF:
		for len(messageBuff) < cfg.bufferSize {
			if scanner.Scan() {
				messageBuff = append(messageBuff, scanner.Text())
			} else {
				done = true
				break BUFF
			}
		}
		outc <- messageBuff
		runtime.Gosched()
		if done {
			close(outc)
			break READ
		}
	}
}

const tform = "02/Jan/2006:15:04:05 +0000"
const regs = `^\[([/: \+\-\w]+)\] ([\w\.\-]+) ("[A-Z]{3,9} (.*) HTTP/\d\.\d") ` +
	`(from: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) .*) to: [, :\w\.\-]* (\d{3}) \d+ ` +
	`"[^"]*" "([\-:;,\(\)\. /\w_]+)" .*`

func work(cfg config) {
	dbw := newDBWorker(cfg.dbPath, cfg.workers*2)
	parsedChan, dbWg := dbw.serve()
	pool := newParsersPool(cfg.workers, regs, parsedChan)
	pool.serve()
	shred(cfg, pool.inc)
	pool.wg.Wait()
	close(pool.outc)
	dbWg.Wait()
}

func main() {
	work(getConfig())
}
