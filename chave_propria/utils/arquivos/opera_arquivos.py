from typing import Any, Dict, List

from fastapi import HTTPException, status

from chave_propria.settings.Settings import log


def escreve_arquivo(arquivo: str, conteudo: List[Any]) -> Dict[str, str]:
    """
    Escreve arquivo no filesystem

    Arguments:
        arquivo (str): Caminho absoluto para o arquivo
        conteudo (List[Any]): O conteúdo que será escrito no arquivo

    Returns:
        Dict[str, str]: Um dicionário informando se a escrita foi concluída

    Raises:
        IOError, OSError: Erro na escrita do arquivo.
        PermissionError: Problemas de permissão para criação do arquivo.
    """
    try:
        with open(arquivo, 'wb') as file:
            try:
                file.writelines(conteudo)
            except (IOError, OSError) as error:
                log.error(f'Erro para escrever no arquivo {arquivo}: {error}')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return {'status': 'ok', 'msg': 'Arquivo criado com sucesso!'}
    except PermissionError:
        log.error(f'Permissão negada para criação do arquivo {arquivo}!')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
