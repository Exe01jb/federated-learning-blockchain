import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from blockchain.deploy import deploy_contract
from blockchain.interface import BlockchainInterface
from fl.client import FederatedClient
from fl.data_utils import load_mnist, make_loader, partition_data
from fl.model import SimpleCNN
from fl.server import FederatedServer

load_dotenv()

NUM_CLIENTS = int(os.getenv("NUM_CLIENTS", "4"))
NUM_ROUNDS = int(os.getenv("NUM_ROUNDS", "3"))
LOCAL_EPOCHS = int(os.getenv("LOCAL_EPOCHS", "1"))
IID = os.getenv("IID", "true").lower() == "true"
GETH_RPC_URL = os.getenv("GETH_RPC_URL", "http://127.0.0.1:8545")


def main():
    print("1. Deploying FederatedLearning contract to Geth...")
    contract_address = deploy_contract()
    chain = BlockchainInterface(rpc_url=GETH_RPC_URL)

    print(f"2. Registering {NUM_CLIENTS} simulated participants on-chain...")
    accounts = chain.w3.eth.accounts[:NUM_CLIENTS]
    for acct in accounts:
        BlockchainInterface(rpc_url=GETH_RPC_URL, account=acct).register_participant()

    print(f"3. Loading and partitioning MNIST across clients ({'IID' if IID else 'non-IID'})...")
    train_set, test_set = load_mnist()
    shards = partition_data(train_set, NUM_CLIENTS, iid=IID)
    clients = [
        FederatedClient(f"client-{i}", SimpleCNN(), make_loader(shards[i]))
        for i in range(NUM_CLIENTS)
    ]

    global_model = SimpleCNN()
    server = FederatedServer(global_model)
    test_loader = make_loader(test_set, shuffle=False)

    global_weights = global_model.state_dict()

    for round_id in range(NUM_ROUNDS):
        print(f"\n--- Round {round_id} ---")
        client_weights, client_sizes = [], []

        for client, acct in zip(clients, accounts):
            weights, n_samples = client.local_train(global_weights, epochs=LOCAL_EPOCHS)
            weight_hash = client.hash_weights(weights)

            BlockchainInterface(rpc_url=GETH_RPC_URL, account=acct).submit_model_update(
                model_hash_hex=weight_hash,
                model_cid=f"ipfs://placeholder-{client.client_id}-round{round_id}",
                data_size=n_samples,
            )
            client_weights.append(weights)
            client_sizes.append(n_samples)
            print(f"  {client.client_id}: submitted update ({n_samples} samples, hash {weight_hash[:10]}...)")

        global_weights = server.federated_average(client_weights, client_sizes)
        global_hash = FederatedClient.hash_weights(global_weights)

        chain.finalize_round(global_hash_hex=global_hash, global_cid=f"ipfs://placeholder-global-round{round_id}")

        accuracy = server.evaluate(test_loader)
        print(f"  Global model accuracy after round {round_id}: {accuracy:.4f}")
        print(f"  Round finalized on-chain, rewards distributed to {len(accounts)} participants.")

    print(f"\nDone. Contract: {contract_address}")


if __name__ == "__main__":
    main()
