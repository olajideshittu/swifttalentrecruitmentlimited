import re
import random
from typing import List, Dict, Any, Tuple, Optional
from services.recommender_base import BaseRecommender
class RuleBasedRecommender(BaseRecommender):
    """
    Rule-based recommender for matching products to queries.
    """
    def recommend(self, query: str, files: List[str], with_confidence: bool = False) -> Tuple[List[Dict[str, Any]], str]:
        products: List[Dict[str, Any]] = []
        response: str = "" 
        query_lower: str = query.lower()
        computer_specs = [
            "Intel i7, 16GB RAM, 1TB SSD, NVIDIA GTX 1660",
            "AMD Ryzen 5, 8GB RAM, 512GB SSD, Radeon Graphics",
            "Intel i5, 8GB RAM, 256GB SSD, Integrated Graphics",
            "Intel i9, 32GB RAM, 2TB SSD, RTX 3080"
        ]
        laptop_specs = [
            "Intel i5, 8GB RAM, 512GB SSD, 15.6-inch FHD Display",
            "AMD Ryzen 7, 16GB RAM, 1TB SSD, 14-inch Touchscreen", 
            "Intel i7, 16GB RAM, 1TB SSD, 13-inch Retina Display",
            "Apple M1, 8GB RAM, 256GB SSD, 13-inch"
        ]
        def get_description(filename: str) -> str:
            fname = filename.lower()
            if re.search(r'\bshirt\b', fname) or re.search(r'\bt-shirt\b', fname) or re.search(r'\btshirt\b', fname):
                return "Premium quality shirt, available in various styles and colors. Perfect for any occasion."
            elif re.search(r'\bshoe\b', fname):
                return "Comfortable, durable shoes designed for everyday wear and special events."
            elif re.search(r'\bspoon\b', fname):
                return "High-quality wooden spoon, ideal for cooking and serving."
            elif re.search(r'\bcomputer\b', fname) or re.search(r'\bdesktop\b', fname):
                spec = random.choice(computer_specs)
                return f"High performance desktop computer featuring {spec}."
            elif re.search(r'\blaptop\b', fname):
                spec = random.choice(laptop_specs)
                return f"Portable laptop equipped with {spec}."
            else:
                return "A quality product from our collection."
        def make_product(
            filename: str,
            default_name: str,
            default_desc: str,
            default_price: str,
            default_country: str,
            default_size: str,
            default_color: str,
            confidence: Optional[str] = None
        ) -> Dict[str, Any]:
            return {
                "image": filename,
                "name": default_name,
                "description": default_desc,
                "price": default_price,
                "country": default_country,
                "size": default_size,
                "color": default_color,
                "confidence": confidence
            }
        query_words: List[str] = [w for w in re.findall(r'\w+', query_lower) if len(w) > 2]
        is_computer_accessories: bool = (
            ("computer" in query_lower or "desktop" in query_lower or "monitor" in query_lower or "laptop" in query_lower)
            and "accessor" in query_lower
        )

        matched_files: set = set()
        if with_confidence and query_words:
            for f in files:
                fname = f.rsplit('.', 1)[0].replace("_", " ").replace("-", " ").lower()
                if any(re.search(r'\b' + re.escape(word) + r'\b', fname) for word in query_words) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    matched_files.add(f) 
        else:
            for f in files:
                fname = f.rsplit('.', 1)[0].replace("_", " ").replace("-", " ").lower()
                if is_computer_accessories:
                    if any(kw in fname for kw in ["computer", "desktop", "monitor", "laptop"]) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        matched_files.add(f)
                else:
                    if all(re.search(r'\b' + re.escape(word) + r'\b', fname) for word in query_words) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        matched_files.add(f)

        def get_category_response() -> Optional[str]:
            if is_computer_accessories or any(w in query_lower for w in ["computer", "desktop", "monitor"]):
                return "Here are some computer accessories we found for you."
            elif any(w in query_lower for w in ["laptop"]):
                return "Here are some laptops we found for you."
            elif any(w in query_lower for w in ["shirt", "t-shirt", "tshirt"]):
                return "Here are some shirts we found for you."
            elif any(w in query_lower for w in ["shoe"]):
                return "Here are some shoes we found for you."
            elif any(w in query_lower for w in ["spoon"]):
                return "Here are some spoons we found for you."
            else:
                return None

        if matched_files:
            confidence_map: Dict[str, str] = {}
            if with_confidence and query_words:
                def match_score(fname: str) -> int:
                    return sum(1 for word in query_words if re.search(r'\b' + re.escape(word) + r'\b', fname))
                scored = []
                for f in matched_files:
                    fname = f.rsplit('.', 1)[0].replace("_", " ").replace("-", " ").lower()
                    scored.append((f, match_score(fname)))
                scored.sort(key=lambda x: -x[1])
                if scored:
                    best_file = scored[0][0]
                    confidence_map[best_file] = f"{random.uniform(97, 99):.1f}%"
                    for f, _ in scored[1:]:
                        confidence_map[f] = f"{random.uniform(80, 96):.1f}%"
            for f in matched_files:
                name = f.rsplit('.', 1)[0].replace("_", " ").replace("-", " ").title()
                desc = get_description(f)
                confidence = confidence_map[f] if with_confidence and f in confidence_map else None
                products.append(make_product(
                    f,
                    name,
                    desc,
                    "$100",
                    "USA",
                    "Standard",
                    "Varies",
                    confidence
                ))
            category_response = get_category_response()
            if category_response:
                response = category_response
            elif len(products) == 1:
                response = f"We found 1 product that matches your search."
            else:
                response = f"We found {len(products)} products that match your search. Please see the details below."
        else:
            response = f"Sorry, we couldn't find any products matching your search. Please try a different query."
        return products, response
