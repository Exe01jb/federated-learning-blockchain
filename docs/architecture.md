# Architecture

## Design goals

1. **Never put raw model weights or raw data on-chain.** Gas costs would be
   prohibitive and it isn't necessary for the trust guarantees we want.
2. **Make every round auditable.** Anyone can replay the chain of
   `ModelUpdateSubmitted` and `RoundFinalized` events and verify that a given
   global model at round *k* really was produced from that round's committed
   updates.
3. **Keep the aggregator role replaceable.** `finalizeRound` is `onlyOwner` in
   this demo for simplicity; in a production system that role could instead
   be a multisig, a DAO vote, or a rotating committee.

## On-chain vs. off-chain

| Data | Where | Why |
|---|---|---|
| Raw training data | Client-local only | Never leaves the device -- this is the entire point of FL |
| Local model weights (per round) | Off-chain (e.g. IPFS), hash on-chain | Full weights are large; the chain only needs a commitment |
| Global model weights (per round) | Off-chain, hash on-chain | Same reasoning |
| Round metadata (who submitted, when, data size, reward) | On-chain | Small, and this is exactly the part that needs to be trust-minimized |

## Round lifecycle

1. `registerParticipant()` -- one-time, per address.
2. The aggregator distributes the current global weights off-chain (in the
   demo, directly in memory; in a real deployment this would also go through
   IPFS/CID so it's independently verifiable by any participant).
3. Each client calls `submitModelUpdate(hash, CID, dataSize)` once per round.
4. Once `roundUpdates[currentRound].length >= minParticipants`, the aggregator
   calls `finalizeRound(globalHash, globalCID)`, which:
   - records the `RoundInfo`
   - pays every contributor of that round an equal share of `rewardPerRound`
   - increments each contributor's on-chain `reputation`
   - advances `currentRound`

## Extending this demo

- **Secure aggregation**: replace the plaintext value returned by
  `local_train` with a masked/encrypted update (e.g. via a secret-sharing
  scheme) so even the aggregator only ever sees the sum, not individual
  client updates.
- **Differential privacy**: add gradient clipping + calibrated noise in
  `FederatedClient.local_train` before returning weights.
- **Reputation-weighted rewards**: change `_distributeRewards` to weight
  payouts by `participants[p].reputation` instead of splitting equally.
- **Non-IID robustness**: `fl/data_utils.partition_data(..., iid=False)`
  already simulates label-skewed clients -- a good starting point for testing
  aggregation strategies beyond plain FedAvg (e.g. FedProx).
- **Public testnet deployment**: swap the unlocked-account `.transact()` calls
  in `blockchain/interface.py` for `build_transaction` + `sign_transaction`
  with a funded private key.
