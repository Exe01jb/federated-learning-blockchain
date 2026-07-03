from typing import List

import torch
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import datasets, transforms


def load_mnist(data_dir: str = "./data"):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),
    ])
    train_set = datasets.MNIST(data_dir, train=True, download=True, transform=transform)
    test_set = datasets.MNIST(data_dir, train=False, download=True, transform=transform)
    return train_set, test_set


def partition_data(dataset: Dataset, num_clients: int, iid: bool = True, seed: int = 42) -> List[Subset]:
    """Split a dataset into `num_clients` shards.

    iid=True:  shuffle then split into equal contiguous chunks (each client
               sees a random, representative sample of all classes).
    iid=False: sort by label first, then split into shards (each client sees
               mostly one or two digits) -- the classic non-IID FL setting
               used to stress-test aggregation strategies.
    """
    n = len(dataset)
    generator = torch.Generator().manual_seed(seed)

    if iid:
        indices = torch.randperm(n, generator=generator).tolist()
    else:
        targets = dataset.targets if hasattr(dataset, "targets") else [dataset[i][1] for i in range(n)]
        indices = sorted(range(n), key=lambda i: int(targets[i]))

    shard_size = n // num_clients
    shards = []
    for c in range(num_clients):
        start = c * shard_size
        end = start + shard_size if c < num_clients - 1 else n
        shards.append(Subset(dataset, indices[start:end]))
    return shards


def make_loader(subset: Dataset, batch_size: int = 32, shuffle: bool = True) -> DataLoader:
    return DataLoader(subset, batch_size=batch_size, shuffle=shuffle)
