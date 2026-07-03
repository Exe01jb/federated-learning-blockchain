"""Thin Web3.py wrapper exposing the FederatedLearning contract's calls as
plain Python methods, used by both the simulation script and tests.
"""

import json
import os
from typing import Optional

from web3 import Web3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOYMENT_PATH = os.path.join(ROOT, "build", "deployment.json")


class BlockchainInterface:
    def __init__(self, rpc_url: str, account: Optional[str] = None, deployment_path: str = DEPLOYMENT_PATH):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        assert self.w3.is_connected(), f"Could not connect to node at {rpc_url}"

        with open(deployment_path) as f:
            deployment = json.load(f)

        self.contract = self.w3.eth.contract(address=deployment["address"], abi=deployment["abi"])
        self.account = account or self.w3.eth.accounts[0]

    def register_participant(self):
        tx_hash = self.contract.functions.registerParticipant().transact({"from": self.account})
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def submit_model_update(self, model_hash_hex: str, model_cid: str, data_size: int):
        model_hash_bytes = bytes.fromhex(model_hash_hex)  # sha256 hexdigest -> 32 bytes (bytes32)
        tx_hash = self.contract.functions.submitModelUpdate(
            model_hash_bytes, model_cid, data_size
        ).transact({"from": self.account})
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def finalize_round(self, global_hash_hex: str, global_cid: str):
        global_hash_bytes = bytes.fromhex(global_hash_hex)
        tx_hash = self.contract.functions.finalizeRound(
            global_hash_bytes, global_cid
        ).transact({"from": self.account})
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_round_updates(self, round_id: int):
        return self.contract.functions.getRoundUpdates(round_id).call()

    def get_participant(self, address: str):
        return self.contract.functions.participants(address).call()

    def current_round(self) -> int:
        return self.contract.functions.currentRound().call()
