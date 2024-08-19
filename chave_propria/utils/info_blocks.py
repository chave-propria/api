from typing import List

from fastapi import UploadFile

from chave_propria.settings.Settings import Settings

config = Settings()

bloco_bytes = config.BLOCO_BYTES


def _bytes_faltantes(tam_arq: int) -> int:
    """
    Função privada utilizada para calcular os bytes faltantes para completar blocos

    Arguments:
        tam_arq (int): O tamanho do arquivo em bytes

    Returns:
        A quantidade de bytes faltantes
    """
    if tam_arq % bloco_bytes == 0:
        return 0

    if tam_arq <= bloco_bytes:
        return bloco_bytes - tam_arq

    return bloco_bytes - (tam_arq % bloco_bytes)


def _bloco_incompleto(bytes_faltantes: int, info: List[str]):
    """
    Função privada utilizada para completar o bloco

    Arguments:
        bytes_faltantes (int): A quantidade de bytes faltantes
        info (List[str]): Os bytes de informação que serão utilizados no bloco

    Returns:
        O bloco de informação completo
    """
    completar_bloco = [70 + _ for _ in range(bytes_faltantes)]

    completar_bloco.extend(info)

    return [
        completar_bloco[item : item + 2]
        for item in range(0, len(completar_bloco), 2)
    ]


def info_blocks(file: UploadFile):
    qnt_blocos = file.size // bloco_bytes
    bytes_faltantes = _bytes_faltantes(tam_arq=file.size)

    blocos = dict()

    if bytes_faltantes:
        leitura_bytes = bloco_bytes - bytes_faltantes
        info = list(file.file.read(leitura_bytes))
        blocos[0] = _bloco_incompleto(
            bytes_faltantes=bytes_faltantes, info=info
        )

    for bloco in range(qnt_blocos):
        blocos[bloco + 1] = list()

        while (len(blocos[bloco + 1]) < 4) and (info := file.file.read(2)):
            blocos[bloco + 1].append(list(info))

    return qnt_blocos, bytes_faltantes, blocos
