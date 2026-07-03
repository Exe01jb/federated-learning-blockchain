import json
import os

import solcx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT_PATH = os.path.join(ROOT, "contracts", "FederatedLearning.sol")
BUILD_DIR = os.path.join(ROOT, "build")
SOLC_VERSION = "0.8.19"


def compile_contract() -> dict:
    solcx.install_solc(SOLC_VERSION)

    with open(CONTRACT_PATH) as f:
        source = f.read()

    compiled = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )
    _, interface = compiled.popitem()

    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(os.path.join(BUILD_DIR, "FederatedLearning.json"), "w") as f:
        json.dump(interface, f, indent=2)

    return interface


if __name__ == "__main__":
    compile_contract()
    print(f"Compiled -> {os.path.join(BUILD_DIR, 'FederatedLearning.json')}")
