from django.shortcuts import render
from elasticsearch_dsl import Search

from .search_indexes import ArticleIndex


def search(request):
    query = request.GET.get("q", "")
    s = Search(using="default", index="articles").query(
        "multi_match", query=query, fields=["title", "content"]
    )
    response = s.execute()
    results = [hit.to_dict() for hit in response]
    return render(request, "search_results.html", {"results": results, "query": query})
