#!/usr/bin/env bash
# Install Geth first: https://geth.ethereum.org/docs/getting-started/installing-geth

set -e

DATA_DIR="${1:-./geth-dev-data}"

geth --dev \
     --http \
     --http.addr 127.0.0.1 \
     --http.port 8545 \
     --http.api eth,net,web3,personal \
     --http.corsdomain "*" \
     --datadir "$DATA_DIR"
