import copy
from typing import Dict, List

import torch
import torch.nn as nn


class FederatedServer:
    def __init__(self, global_model: nn.Module):
        self.global_model = global_model

    def federated_average(
        self, client_weights_list: List[Dict[str, torch.Tensor]], client_sizes: List[int]
    ) -> Dict[str, torch.Tensor]:
        total = sum(client_sizes)
        avg = copy.deepcopy(client_weights_list[0])

        for key in avg:
            avg[key] = torch.zeros_like(avg[key], dtype=torch.float32)

        for weights, size in zip(client_weights_list, client_sizes):
            w = size / total
            for key in avg:
                avg[key] += weights[key].float() * w

        self.global_model.load_state_dict(avg)
        return avg

    def evaluate(self, test_loader, device: str = "cpu") -> float:
        self.global_model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                preds = self.global_model(data).argmax(dim=1)
                correct += (preds == target).sum().item()
                total += target.size(0)
        return correct / total
