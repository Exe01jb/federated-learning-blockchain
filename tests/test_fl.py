"""Unit tests for the FedAvg aggregation logic (no blockchain or dataset
download required).
"""

import torch

from fl.model import SimpleCNN
from fl.server import FederatedServer


def test_federated_average_matches_manual_weighted_mean():
    model = SimpleCNN()
    server = FederatedServer(model)

    w1 = {k: torch.ones_like(v) for k, v in model.state_dict().items()}
    w2 = {k: torch.zeros_like(v) for k, v in model.state_dict().items()}

    # client 1 has 3x more data than client 2 -> should dominate the average
    avg = server.federated_average([w1, w2], client_sizes=[300, 100])

    for key in avg:
        expected = w1[key] * 0.75 + w2[key] * 0.25
        assert torch.allclose(avg[key], expected, atol=1e-6)


def test_federated_average_equal_weights_is_simple_mean():
    model = SimpleCNN()
    server = FederatedServer(model)

    w1 = {k: torch.full_like(v, 2.0) for k, v in model.state_dict().items()}
    w2 = {k: torch.full_like(v, 4.0) for k, v in model.state_dict().items()}

    avg = server.federated_average([w1, w2], client_sizes=[50, 50])

    for key in avg:
        assert torch.allclose(avg[key], torch.full_like(avg[key], 3.0), atol=1e-6)
