"""
Search utilities
................
"""

# TODO: This module should be redesigned with higher level of
# abstraction, like consuming/producing pydantic models (instead of
# native dicts and lists) for additional type safety.

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
async def update(index: str, obj_id: uuid.UUID, attrs: typing.Mapping[str, typing.Any]):
    """Update a document in the index

    Parameters:
        index: The name of the index
        obj_id: The index of the object to update
        attrs: The attributes to replace the old ones
    """
    await _es.update(index, str(obj_id), {"doc": attrs})


# pylint: disable=redefined-outer-name
async def remove(index: str, obj_id: uuid.UUID, path: typing.List[str]):
    """Remove an object or a field withing the objec

    Parameters:
        index: The name of the index
        obj_id: The id of the object to (partially) remove
        path: The path of the subobject, or empty list if the whole
              object is removed
    """
    # TODO: Do it atomically
    obj_id = str(obj_id)
    if path:
        source = await _es.get_source(index, obj_id)
        subobj = source
        for k in path[:-1]:
            subobj = source.get(k, None)
            if not subobj:
                return
        subobj.pop(path[-1], None)
    await _es.delete(index, obj_id)
    if path:
        await _es.create(index, obj_id, source)


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
