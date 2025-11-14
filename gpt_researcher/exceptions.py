"""
Custom exceptions for GPT Researcher.
"""


class TavilyAPIError(Exception):
    """
    Raised when Tavily API returns an error response.

    This exception is used to distinguish between API failures and
    legitimate "no results found" scenarios when using the Tavily search retriever.

    Attributes:
        message: Error message describing the failure
        status_code: HTTP status code from Tavily API (e.g., 400, 401, 500)
        query_length: Length of the query that caused the error (useful for diagnosing query-too-long issues)
    """

    def __init__(self, message: str, status_code: int = None, query_length: int = None):
        """
        Initialize TavilyAPIError.

        Args:
            message: Error message describing what went wrong
            status_code: HTTP status code from the API response
            query_length: Character length of the query that failed
        """
        self.status_code = status_code
        self.query_length = query_length
        super().__init__(message)
