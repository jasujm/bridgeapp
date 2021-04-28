"""
Search utilities
................
"""

# Until elasticsearch_dsl supports asyncio, run everything in thread pool

import typing
import uuid

import fastapi.concurrency as fc
import elasticsearch_dsl
import elasticsearch_dsl.query as esq

DocType = typing.Type[elasticsearch_dsl.Document]


async def index(doc: elasticsearch_dsl.Document, doc_id: uuid.UUID):
    """Index a document

    Parameters:
        doc: The document to index
        doc_id: The id of the document
    """
    doc.meta.id = doc_id
    await fc.run_in_threadpool(doc.save)


async def update(doc: elasticsearch_dsl.Document, doc_id: uuid.UUID):
    """Update a document in the index

    Parameters:
        doc: The document updates
        doc_id: The id of the document to update
    """
    doc_type = type(doc)
    old_doc = await fc.run_in_threadpool(doc_type.get, id=doc_id)
    await fc.run_in_threadpool(old_doc.update, **doc.to_dict())


async def remove(doc_type: DocType, doc_id: uuid.UUID, path: typing.List[str] = None):
    """Remove an object or a field within an object from the index

    Parameters:
        doc_type: The type of the document to remove
        doc_id: The id of the document to update
        path: The path of the subdocument, or empty list if the whole
              object is removed

    """
    doc = await fc.run_in_threadpool(doc_type.get, id=doc_id)
    if path:
        # Can this be done atomically?
        subdoc = doc
        for k in path[:-1]:
            subdoc = getattr(subdoc, k, None)
            if not subdoc:
                return
        subdoc[path[-1]] = None
        await fc.run_in_threadpool(doc.save)
    else:
        await fc.run_in_threadpool(doc.delete)


async def search(doc_type: DocType, q: str) -> typing.List[elasticsearch_dsl.Document]:
    """Search for previously indexed documents

    Parameters:
        doc_type: The type of the document to search
        q: The query string

    Returns:
        List of tuples containing index and attributes of the found objects
    """
    s = doc_type.search().query(esq.MultiMatch(query=q))
    return await fc.run_in_threadpool(s.execute)
