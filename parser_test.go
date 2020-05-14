package main

import (
	"testing"
)

// BechmarkMain just bechmark
func BenchmarkMain(b *testing.B) {
	work(
		config{
			inputFile:  "/home/vbadaev/Nextcloud/go/4fun/parser/proxy.staging-zabbix.tradingview.com.access.log",
			dbPath:     "result.db",
			workers:    4,
			bufferSize: 100,
		},
	)
}
