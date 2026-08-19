from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask.views import MethodView
import os
import logging
from services.recommendation_service import RecommendationService
from services.ocr_service import OCRService

app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = "change-this-in-production"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

recommendation_service = RecommendationService()
ocr_service = OCRService()

class ProductRecommendationAPI(MethodView):
    """
    API endpoint for product recommendations based on a text query.
    """  
    def post(self) -> 'flask.wrappers.Response':
        """
        Handle POST request for product recommendations.

        Returns:
            flask.Response: JSON response with recommended products and response message.
        """
        try:
            query: str = request.form.get('query', '')
            logger.info("Received product recommendation request: %s", query)
            if not isinstance(query, str) or len(query) > 256:
                logger.warning("Invalid query received: %s", query)
                return jsonify({"error": "Invalid query"}), 400
            products, response = recommendation_service.recommend_products(query)
            logger.info("Recommendation successful for query: %s", query)
            return jsonify({"products": products, "response": response})
        except Exception as e:
            logger.error("Error in ProductRecommendationAPI: %s", str(e))
            return jsonify({"error": "Internal server error"}), 500

class OCRQueryAPI(MethodView):
    """
    API endpoint for extracting text from an uploaded image and recommending products.
    """
    def post(self) -> 'flask.wrappers.Response':
        """
        Handle POST request for OCR-based product recommendations.

        Returns:
            flask.Response: JSON response with recommended products, response message, and extracted text.
        """
        try:
            image_file = request.files.get('image_data')
            if not image_file or not hasattr(image_file, "filename"):
                logger.warning("No image uploaded in OCRQueryAPI")
                return jsonify({"error": "No image uploaded"}), 400
            logger.info("Received OCR query for image: %s", getattr(image_file, "filename", "unknown"))
            extracted_text = ocr_service.extract_text(image_file)
            def is_meaningful(text: str) -> bool:
                """
                Check if the extracted text is meaningful.

                Args:
                    text (str): The text to check.

                Returns:
                    bool: True if meaningful, False otherwise.
                """
                import re
                if not text or not text.strip():
                    return False
                alnum = re.sub(r'[^a-zA-Z0-9]', '', text)
                return len(alnum) > 2

            filename = image_file.filename
            fallback_query = os.path.splitext(os.path.basename(filename))[0] if filename else ""
            if is_meaningful(extracted_text):
                query = extracted_text
                display_text = extracted_text
            else:
                query = fallback_query
                display_text = ""
            products, response = recommendation_service.recommend_products(query)
            logger.info("OCR recommendation successful for query: %s", query)
            return jsonify({"products": products, "response": response, "extracted_text": display_text})
        except Exception as e:
            logger.error("Error in OCRQueryAPI: %s", str(e))
            return jsonify({"error": "Internal server error"}), 500

class ImageProductSearchAPI(MethodView):
    """
    API endpoint for searching products by uploaded image.
    """
    def post(self) -> 'flask.wrappers.Response':
        """
        Handle POST request for product search by image.

        Returns:
            flask.Response: JSON response with recommended products and response message.
        """
        try:
            product_image = request.files.get('product_image')
            product_name = request.form.get('product_name', '').strip()
            if not product_image or not hasattr(product_image, "filename"):
                logger.warning("No image uploaded in ImageProductSearchAPI")
                return jsonify({"error": "No image uploaded"}), 400
            logger.info("Received image product search for image: %s", getattr(product_image, "filename", "unknown"))
            predictions = []  # Placeholder for CNN logic if needed
            # For now, just use filename as category
            filename = product_image.filename
            category = os.path.splitext(os.path.basename(filename))[0] if filename else ""
            products, response = recommendation_service.recommend_products(category)
            logger.info("Image product search recommendation successful for category: %s", category)
            return jsonify({
                "products": products,
                "response": response
            })
        except Exception as e:
            logger.error("Error in ImageProductSearchAPI: %s", str(e))
            return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def home() -> 'flask.wrappers.Response':
    """
    Redirect to the text query page.

    Returns:
        flask.Response: Redirect response.
    """
    return redirect(url_for('text_query_page'))

@app.route('/text-query', methods=['GET', 'POST'])
def text_query_page() -> 'flask.wrappers.Response':
    """
    Render the text query page and handle product recommendation requests.

    Returns:
        flask.Response: Rendered HTML page.
    """
    response = None
    products = []
    try:
        if request.method == 'POST':
            query = request.form.get('query', '')
            logger.info("Text query page POST with query: %s", query)
            if not isinstance(query, str) or len(query) > 256:
                logger.warning("Invalid query on text_query_page: %s", query)
                response = "Invalid query."
            else:
                products, response = recommendation_service.recommend_products(query)
                logger.info("Text query recommendation successful for query: %s", query)
        return render_template('text_query.html', products=products, response=response)
    except Exception as e:
        logger.error("Error in text_query_page: %s", str(e))
        return render_template('text_query.html', products=[], response="Internal server error")

@app.route('/ocr-query-page', methods=['GET', 'POST'])
def ocr_query_page() -> 'flask.wrappers.Response':
    """
    Render the OCR query page and handle product recommendation requests based on extracted text from image.

    Returns:
        flask.Response: Rendered HTML page.
    """
    response = None
    products = []
    extracted_text = ""
    uploaded_filename = ""
    try:
        if request.method == 'POST':
            image_file = request.files.get('image_data')
            if not image_file or not hasattr(image_file, "filename"):
                logger.warning("No image uploaded on ocr_query_page")
                response = "No image uploaded."
            else:
                logger.info("OCR query page POST with image: %s", getattr(image_file, "filename", "unknown"))
                extracted_text = ocr_service.extract_text(image_file)
                def is_meaningful(text: str) -> bool:
                    """
                    Check if the extracted text is meaningful.

                    Args:
                        text (str): The text to check.

                    Returns:
                        bool: True if meaningful, False otherwise.
                    """
                    import re
                    if not text or not text.strip():
                        return False
                    alnum = re.sub(r'[^a-zA-Z0-9]', '', text)
                    return len(alnum) > 2

                filename = image_file.filename
                uploaded_filename = filename
                fallback_query = os.path.splitext(os.path.basename(filename))[0] if filename else ""
                if is_meaningful(extracted_text):
                    query = extracted_text
                    display_text = extracted_text
                    show_extracted = True
                else:
                    query = fallback_query
                    display_text = ""
                    show_extracted = False
                products, response = recommendation_service.recommend_products(query)
                logger.info("OCR query page recommendation successful for query: %s", query)
        else:
            show_extracted = False
            display_text = ""
        return render_template(
            'ocr_query.html',
            products=products,
            response=response,
            extracted_text=display_text if show_extracted else "",
            uploaded_filename=uploaded_filename
        )
    except Exception as e:
        logger.error("Error in ocr_query_page: %s", str(e))
        return render_template(
            'ocr_query.html',
            products=[],
            response="Internal server error",
            extracted_text="",
            uploaded_filename=""
        )

@app.route('/product-image-upload', methods=['GET', 'POST'])
def product_image_upload_page() -> 'flask.wrappers.Response':
    """
    Render the product image upload page and handle product recommendation requests based on uploaded image.

    Returns:
        flask.Response: Rendered HTML page.
    """
    response = None
    products = []
    try:
        if request.method == 'POST':
            product_image = request.files.get('product_image')
            product_name = request.form.get('product_name', '').strip()
            if not product_image or not hasattr(product_image, "filename"):
                logger.warning("No image uploaded on product_image_upload_page")
                response = "No image uploaded."
            else:
                logger.info("Product image upload page POST with image: %s", getattr(product_image, "filename", "unknown"))
                filename = product_image.filename
                category = os.path.splitext(os.path.basename(filename))[0] if filename else ""
                # Pass with_confidence=True for CNN/Product Image Upload
                products, response = recommendation_service.recommend_products(category, with_confidence=True)
                logger.info("Product image upload recommendation successful for category: %s", category)
        return render_template('product_image_upload.html', products=products, response=response)
    except Exception as e:
        logger.error("Error in product_image_upload_page: %s", str(e))
        return render_template('product_image_upload.html', products=[], response="Internal server error")

@app.route('/sample_response', methods=['GET'])
def sample_response() -> 'flask.wrappers.Response':
    """
    Render a sample response page.

    Returns:
        flask.Response: Rendered HTML page.
    """
    return render_template('sample_response.html')

app.add_url_rule('/product-recommendation', view_func=ProductRecommendationAPI.as_view('product_recommendation_api'))
app.add_url_rule('/ocr-query', view_func=OCRQueryAPI.as_view('ocr_query_api'))
app.add_url_rule('/image-product-search', view_func=ImageProductSearchAPI.as_view('image_product_search_api'))

@app.route('/product/<product_name>')
def product_detail(product_name: str) -> 'flask.wrappers.Response':
    """
    Render the product detail page for a given product.

    Args:
        product_name (str): The name of the product.

    Returns:
        flask.Response: Rendered HTML page or 404 if not found.
    """
    try:
        # Find the product in the static folder
        import os
        from services.recommendation_service import RecommendationService
        rec_service = RecommendationService()
        static_dir = "static"
        files = os.listdir(static_dir)
        matched_file = None
        logger.info("Requested product detail for: %s", product_name)
        for f in files:
            if product_name.lower() == os.path.splitext(f)[0].replace(" ", "_").lower():
                matched_file = f
                break
        if matched_file:
            # Use the same get_description logic as in RecommendationService
            def get_description(filename: str) -> str:
                """
                Get a description for the product based on filename.

                Args:
                    filename (str): The filename of the product image.

                Returns:
                    str: Product description.
                """
                fname = filename.lower()
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
                import re, random
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

            desc = get_description(matched_file)
            product = {
                "image": matched_file, 
                "name": product_name.replace("_", " ").replace("-", " ").title(),
                "description": desc,
                "price": "$100",
                "country": "USA",
                "size": "Standard",
                "color": "Varies"
            }
            logger.info("Product detail found for: %s", product_name)
            return render_template('product_detail.html', product=product)
        else:
            logger.warning("Product not found: %s", product_name)
            return "Product not found", 404
    except Exception as e:
        logger.error("Error in product_detail: %s", str(e))
        return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True)
