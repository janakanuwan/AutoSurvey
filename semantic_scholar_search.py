# coding=utf-8

# install `pip install semanticscholar`

# ref: https://pypi.org/project/semanticscholar/

from semanticscholar import SemanticScholar

sch = SemanticScholar(timeout=10)

# s2_api_key = '40-CharacterPrivateKeyProvidedToPartners'
# sch = SemanticScholar(api_key=s2_api_key)

key_words = 'Computing Machinery and Intelligence'
_FIELDS = ['DOI', 'title', 'year', 'abstract', 'authors', 'citationCount']

results = sch.search_paper(key_words)
print(f'Total result count: {results.total}')
print(f'First result in details: {results[0]}')
for item in results.items:
    print(item.title)
