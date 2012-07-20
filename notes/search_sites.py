import haystack
# Signal haystack to search through app directories for search_indexes.py,
# registering all SearchIndexes with SearchSite
haystack.autodiscover()
