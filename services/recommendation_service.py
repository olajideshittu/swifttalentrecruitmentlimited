import os
import logging
from typing import List, Dict, Tuple, Any
from services.rule_based_recommender import RuleBasedRecommender

class RecommendationService:
    """
    Service for recommending products based on a query string.
    Delegates to a modular recommender (e.g., rule-based, ML-based).
    """
    def __init__(self):
        self.recommender = RuleBasedRecommender()

    def recommend_products(self, query: str, with_confidence: bool = False) -> Tuple[List[Dict[str, Any]], str]:
        """
        Recommend products based on the input query.

        Args:
            query (str): The search query.
            with_confidence (bool, optional): Whether to include confidence scores (for CNN/Product Image Upload). Defaults to False.

        Returns:
            Tuple[List[Dict[str, Any]], str]: A list of product dictionaries and a response message.
        """
        try:
            static_dir: str = "static"
            files: List[str] = os.listdir(static_dir)
            products, response = self.recommender.recommend(query, files, with_confidence=with_confidence)
            logging.info("Recommendation successful for query: %s, products found: %d", query, len(products))
            return products, response
        except Exception as e:
            logging.error("Error in recommend_products: %s", str(e))
            return [], "Internal server error"
