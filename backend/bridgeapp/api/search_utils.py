"""
Search utilities
................
"""


import typing
import uuid

import elasticsearch

from bridgeapp.settings import settings


_es = elasticsearch.AsyncElasticsearch(hosts=[settings.elasticsearch_host])


# pylint: disable=redefined-outer-name
async def index(index: str, obj_id: uuid.UUID, attrs: typing.Mapping[str, typing.Any]):
    """Index a document

    Parameters:
        index: The name of the index
        obj_id: The id of the object to index
        attrs: The objet attributes
    """
    await _es.index(index, attrs, id=str(obj_id))


# pylint: disable=redefined-outer-name
async def search(
    index: str, q: str
) -> typing.List[typing.Tuple[uuid.UUID, typing.Dict[str, typing.Any]]]:
    """Search for previously indexed documents

    Parameters:
        index: The name of the index
        q: The query string

    Returns:
        List of tuples containing index and attributes of the found objects
    """
    res = await _es.search({"query": {"multi_match": {"query": q}}}, index)
    return [(uuid.UUID(hits["_id"]), hits["_source"]) for hits in res["hits"]["hits"]]
