import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from chave_propria.settings.Settings import Settings
from chave_propria.utils.arquivos.escreve_chaves import escreve_chave
from chave_propria.utils.info_blocks import info_blocks

config = Settings()

router = APIRouter(prefix='/remetente', tags=['Cifra'])


@router.post(
    '/cifra',
    status_code=HTTPStatus.CREATED,
    description='Realiza a cifração de arquivos do lado do Remetente',
)
def cifra(file: Annotated[UploadFile, File()]):
    chave_arquivo = os.path.join(config.KEYS_PATH, 'minha_chave.txt')
    chave = escreve_chave(arquivo=chave_arquivo)

    qnt_blocos, qnt_bytes_bloco_incompleto, blocos = info_blocks(file=file)
    file.file.close()

    return {
        'Quantidade_Blocos': qnt_blocos,
        'Quantidade_Bytes_Bloco_Incompleto': qnt_bytes_bloco_incompleto,
        'Bloco': blocos,
        'Chave': chave,
    }
