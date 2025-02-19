import os
import json
import requests
import concurrent.futures
import logging
from typing import Dict, List


SEARCH1API_KEY =  "24D015CE-0B18-45CE-97A1-925EA15BE2DF"

def search(query_list: List[str], n_max_doc: int = 20, search_engine: str = 'search1api', freshness: str = '') -> List[Dict[str, str]]:
    doc_lists = []
    for query in query_list:
        try:
            results = search_single(query, search_engine, freshness)
            if results:
                doc_lists.append(results)
        except Exception as e:
            logging.error(f'Search failed for query "{query}": {str(e)}')
            continue
    
    doc_list = _rearrange_and_dedup([d for d in doc_lists if d])
    return doc_list[:n_max_doc]


def search_single(query: str, search_engine: str, freshness: str = '') -> List[Dict[str, str]]:
    try:
        if search_engine == 'search1api':
            search_results = search1api_request(query, freshness=freshness)
            return search1api_format_results(search_results)
        else:
            raise ValueError(f'Unsupported Search Engine: {search_engine}')
    except Exception as e:
        logging.error(f'Search failed: {str(e)}')
        raise ValueError(f'Search failed: {str(e)}')


def search1api_request(query: str, count: int = 50, freshness: str = '') -> List[Dict[str, str]]:
    endpoint = "https://api.search1api.com/search"
    headers = {
        'Authorization': f'Bearer {SEARCH1API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'query': f"{query} timeline news",  # Add timeline and news to get more relevant results
        'search_service': 'google',
        'max_results': count,
        'crawl_results': 5,
        'image': False,
        'gl': 'us',
        'hl': 'en'
    }
    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            logging.warning(f"No results found for query: {query}")
            return []
            
        results = data.get('results', [])
        if not isinstance(results, list):
            logging.error(f"Unexpected results format: {type(results)}")
            return []
            
        return results
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return []


def search1api_format_results(search_results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    formatted_results = []
    for result in search_results:
        if isinstance(result, dict):
            content = result.get('snippet', result.get('description', ''))
            if not content and result.get('content'):
                content = result['content']
            
            # Extract date from the result or use a default date
            from datetime import datetime
            import re
            
            # Look for date patterns in URL and title
            text_to_search = f"{result.get('url', '')} {result.get('title', '')}"
            date_pattern = r'(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|20\d{2}[-/]\d{1,2})'
            date_match = re.search(date_pattern, text_to_search)
            
            if date_match:
                date_str = date_match.group(1).replace('/', '-')
                if date_str.count('-') == 1:
                    date_str += '-01'  # Add day if only year-month
                timestamp = f"{date_str}T00:00:00"
            else:
                timestamp = datetime.now().strftime('%Y-%m-%dT00:00:00')  # Use current date as fallback
            
            formatted_result = {
                'title': result.get('title', ''),
                'snippet': content,
                'content': content,
                'url': result.get('link', result.get('url', '')),
                'timestamp': timestamp
            }
            if all(v for k, v in formatted_result.items() if k != 'timestamp'):  # Allow empty timestamp
                formatted_results.append(formatted_result)
    return formatted_results


def _rearrange_and_dedup(doc_lists: List[List[Dict[str, str]]]) -> List[Dict[str, str]]:
    doc_list = []
    snippet_set = set()
    # print([len(i) for i in doc_lists])
    for i in range(50):
        for ds in doc_lists:
            if i < len(ds):
                if 'snippet' in ds[i]:
                    signature = ds[i]['snippet'].replace(' ', '')[:200]
                else:
                    signature = ds[i]['content'].replace(' ', '')[:200]
                if signature not in snippet_set:
                    doc_list.append(ds[i])
                    snippet_set.add(signature)
    return doc_list


if __name__ == '__main__':
    queries = ["egypt crisis timeline"]
    from pprint import pprint
    pprint(search(queries, search_engine='search1api', n_max_doc=30))