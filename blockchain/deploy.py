"""Deploys the compiled FederatedLearning contract to a Geth node (local dev
node, or any network reachable via GETH_RPC_URL) using Web3.py.

Uses an unlocked account + `.transact()`, which is what Geth's `--dev` mode
gives you for free. Pointing this at a remote node instead (e.g. a testnet)
means switching to `build_transaction` + `sign_transaction` with a private
key from `.env`, since remote nodes won't have unlocked accounts.
"""

import json
import os

from dotenv import load_dotenv
from web3 import Web3

from blockchain.compile import compile_contract

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(ROOT, "build")

GETH_RPC_URL = os.getenv("GETH_RPC_URL", "http://127.0.0.1:8545")
MIN_PARTICIPANTS = int(os.getenv("MIN_PARTICIPANTS", "2"))
REWARD_PER_ROUND = int(os.getenv("REWARD_PER_ROUND", "1000"))


def deploy_contract() -> str:
    interface_path = os.path.join(BUILD_DIR, "FederatedLearning.json")
    if not os.path.exists(interface_path):
        interface = compile_contract()
    else:
        with open(interface_path) as f:
            interface = json.load(f)

    w3 = Web3(Web3.HTTPProvider(GETH_RPC_URL))
    assert w3.is_connected(), f"Could not connect to Geth at {GETH_RPC_URL}"

    deployer = w3.eth.accounts[0]

    Contract = w3.eth.contract(abi=interface["abi"], bytecode=interface["bin"])
    tx_hash = Contract.constructor(MIN_PARTICIPANTS, REWARD_PER_ROUND).transact({"from": deployer})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    deployment = {"address": receipt.contractAddress, "abi": interface["abi"]}
    with open(os.path.join(BUILD_DIR, "deployment.json"), "w") as f:
        json.dump(deployment, f, indent=2)

    print(f"FederatedLearning deployed at {receipt.contractAddress}")
    return receipt.contractAddress


if __name__ == "__main__":
    deploy_contract()
