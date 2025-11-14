# Tavily API Retriever

# libraries
import os
from typing import Literal, Sequence, Optional
import requests
import json

from ...exceptions import TavilyAPIError


class TavilySearch:
    """
    Tavily API Retriever
    """

    def __init__(self, query, headers=None, topic="general", query_domains=None, strict_mode=False):
        """
        Initializes the TavilySearch object.

        Args:
            query (str): The search query string.
            headers (dict, optional): Additional headers to include in the request. Defaults to None.
            topic (str, optional): The topic for the search. Defaults to "general".
            query_domains (list, optional): List of domains to include in the search. Defaults to None.
            strict_mode (bool, optional): If True, raise TavilyAPIError on API failures instead of returning empty results. Defaults to False.
        """
        self.query = query
        self.headers = headers or {}
        self.topic = topic
        self.base_url = "https://api.tavily.com/search"
        self.api_key = self.get_api_key()
        self.headers = {
            "Content-Type": "application/json",
        }
        self.query_domains = query_domains or None
        self.strict_mode = strict_mode

    def get_api_key(self):
        """
        Gets the Tavily API key
        Returns:

        """
        api_key = self.headers.get("tavily_api_key")
        if not api_key:
            try:
                api_key = os.environ["TAVILY_API_KEY"]
            except KeyError:
                print(
                    "Tavily API key not found, set to blank. If you need a retriver, please set the TAVILY_API_KEY environment variable."
                )
                return ""
        return api_key


    def _search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: str = "general",
        days: int = 2,
        max_results: int = 10,
        include_domains: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        use_cache: bool = True,
    ) -> dict:
        """
        Internal search method to send the request to the API.
        """

        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "days": days,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_images": include_images,
            "api_key": self.api_key,
            "use_cache": use_cache,
        }

        response = requests.post(
            self.base_url, data=json.dumps(data), headers=self.headers, timeout=100
        )

        if response.status_code == 200:
            return response.json()
        else:
            # In strict mode, raise TavilyAPIError with diagnostic information
            if self.strict_mode:
                query_length = len(query)
                error_msg = f"Tavily API returned status {response.status_code}: {response.text}"

                # Add helpful diagnostic for common 400 error (query too long)
                if response.status_code == 400 and query_length > 400:
                    error_msg += f"\n\nQuery length: {query_length} characters (Tavily limit is ~400-500 characters)"
                    error_msg += f"\nTip: Shorten your --task query or let deep research mode handle the details"

                raise TavilyAPIError(error_msg, status_code=response.status_code, query_length=query_length)
            else:
                # Default behavior: raise HTTPError (will be caught by search() method)
                response.raise_for_status()

    def search(self, max_results=10):
        """
        Searches the query
        Returns:

        """
        try:
            # Search the query
            results = self._search(
                self.query,
                search_depth="basic",
                max_results=max_results,
                topic=self.topic,
                include_domains=self.query_domains,
            )
            sources = results.get("results", [])
            if not sources:
                raise Exception("No results found with Tavily API search.")
            # Return the results
            search_response = [
                {"href": obj["url"], "body": obj["content"]} for obj in sources
            ]
        except TavilyAPIError:
            # In strict mode, let TavilyAPIError propagate to caller
            # This allows the CLI to catch it and display a helpful error message
            raise
        except Exception as e:
            # Default behavior: log error and return empty results (backward compatible)
            print(f"Error: {e}. Failed fetching sources. Resulting in empty response.")
            search_response = []
        return search_response
