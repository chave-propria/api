from typing import Dict

from chave_propria.utils.arquivos.opera_arquivos import escreve_arquivo
from chave_propria.utils.idea.chaves import gerar_chave


def escreve_chave(arquivo: str) -> Dict[str, str]:
    """
    Escreve chaves, em bytes, no arquivo.

    Arguments:
        arquivo (str): O caminho completo para o arquivo

    Returns:
        Um dicionário informando se a escrita foi concluída
    """
    chave = gerar_chave()
    escreve_arquivo(arquivo=arquivo, conteudo=chave)

    return {'status': 'ok', 'msg': 'arquivo escrito com sucesso!'}
