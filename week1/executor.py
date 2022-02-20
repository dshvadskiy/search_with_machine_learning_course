#Searches an index with a custom query
from typing import Optional, List
from week1.opensearch import get_opensearch

def search(
    index_name: str,
    from_: int,
    size: int,
    explain: bool = False,
    source: Optional[List[str]] = None,
    query: Optional[str] = None,
    q: Optional[str] = None,
):
    conn = get_opensearch()
    payload = {
        "from_": from_,
        "size": size,
        "explain": explain,
        "_source": source,
        "body": query,
        "q": q,
    }
    r = conn.search(
        index=index_name,
        **payload,
    )
    return r