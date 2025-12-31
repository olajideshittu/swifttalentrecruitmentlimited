from typing import List, Dict, Any, Tuple
import abc

class BaseRecommender(abc.ABC):
    """
    Abstract base class for all recommenders.
    """
    @abc.abstractmethod
    def recommend(self, query: str, files: List[str], **kwargs) -> Tuple[List[Dict[str, Any]], str]:
        """
        Recommend products based on the query and available files.

        Args:
            query (str): The search query.
            files (List[str]): List of available product image filenames.

        Returns:
            Tuple[List[Dict[str, Any]], str]: List of product dicts and a response message.
        """
        pass
