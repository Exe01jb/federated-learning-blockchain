#!/usr/bin/env bash
# Starts a local Geth node in --dev mode: instant mining, one pre-funded and
# unlocked account, JSON-RPC exposed on 127.0.0.1:8545. Enough for the whole
# demo (compile -> deploy -> run_simulation) without needing testnet ETH.
#
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
