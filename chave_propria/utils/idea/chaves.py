from random import randint
from typing import List


def gerar_chave() -> List[bytes]:
    """
    Gera 78 sub-chaves pseudoaleatórias para o algoritmo.

    Returns:
        List[bytes]: Uma lista com os bytes da chave
    """
    chave = [randint(1, 65536).to_bytes(2, 'little') for _ in range(78)]
    return chave
