#!/bin/bash
apt-get update
apt-get install -y nmap
# Install subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
