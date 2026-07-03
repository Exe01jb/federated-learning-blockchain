import copy
import hashlib
import io
from typing import Dict, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader


class FederatedClient:
    def __init__(self, client_id: str, model: nn.Module, train_loader: DataLoader, device: str = "cpu"):
        self.client_id = client_id
        self.model = copy.deepcopy(model).to(device)
        self.train_loader = train_loader
        self.device = device

    def local_train(
        self, global_weights: Dict[str, torch.Tensor], epochs: int = 1, lr: float = 0.01
    ) -> Tuple[Dict[str, torch.Tensor], int]:
        """Load the current global weights, train locally, and return the
        updated weights plus the number of samples used (for weighted
        aggregation on the server).
        """
        self.model.load_state_dict(global_weights)
        self.model.train()

        optimizer = optim.SGD(self.model.parameters(), lr=lr, momentum=0.9)
        criterion = nn.CrossEntropyLoss()

        for _ in range(epochs):
            for data, target in self.train_loader:
                data, target = data.to(self.device), target.to(self.device)
                optimizer.zero_grad()
                loss = criterion(self.model(data), target)
                loss.backward()
                optimizer.step()

        num_samples = len(self.train_loader.dataset)
        return copy.deepcopy(self.model.state_dict()), num_samples

    @staticmethod
    def hash_weights(state_dict: Dict[str, torch.Tensor]) -> str:
        """Deterministic sha256 commitment of a state_dict -- this is what
        gets submitted on-chain as proof that a specific set of weights was
        produced, without ever putting the weights themselves on-chain.
        """
        buffer = io.BytesIO()
        torch.save(state_dict, buffer)
        return hashlib.sha256(buffer.getvalue()).hexdigest()
