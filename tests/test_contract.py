import os

import pytest

from blockchain.deploy import deploy_contract
from blockchain.interface import BlockchainInterface

GETH_RPC_URL = os.getenv("GETH_RPC_URL", "http://127.0.0.1:8545")
FAKE_HASH = "11" * 32  # 32-byte placeholder standing in for a real sha256 model hash


@pytest.fixture(scope="module")
def chain():
    deploy_contract()
    return BlockchainInterface(rpc_url=GETH_RPC_URL)


def test_participant_can_register(chain):
    receipt = chain.register_participant()
    assert receipt.status == 1

    participant = chain.get_participant(chain.account)
    assert participant[0] is True  # registered flag


def test_round_finalizes_after_min_participants_submit(chain):
    # `chain` (accounts[0]) is already registered by the previous test.
    chain.submit_model_update(FAKE_HASH, "ipfs://test-cid-1", data_size=100)

    second = BlockchainInterface(rpc_url=GETH_RPC_URL, account=chain.w3.eth.accounts[1])
    second.register_participant()
    second.submit_model_update(FAKE_HASH, "ipfs://test-cid-2", data_size=50)

    receipt = chain.finalize_round(FAKE_HASH, "ipfs://global-cid")
    assert receipt.status == 1
    assert chain.current_round() == 1
