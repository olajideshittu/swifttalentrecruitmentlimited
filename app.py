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
    def post(self):
        query = request.form.get('query', '')
        if not isinstance(query, str) or len(query) > 256:
            return jsonify({"error": "Invalid query"}), 400
        products, response = recommendation_service.recommend_products(query)
        return jsonify({"products": products, "response": response})

class OCRQueryAPI(MethodView):
    def post(self):
        image_file = request.files.get('image_data')
        if not image_file or not hasattr(image_file, "filename"):
            return jsonify({"error": "No image uploaded"}), 400
        extracted_text = ocr_service.extract_text(image_file)
        def is_meaningful(text):
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
        return jsonify({"products": products, "response": response, "extracted_text": display_text})

class ImageProductSearchAPI(MethodView):
    def post(self):
        product_image = request.files.get('product_image')
        product_name = request.form.get('product_name', '').strip()
        if not product_image or not hasattr(product_image, "filename"):
            return jsonify({"error": "No image uploaded"}), 400
        predictions = []  # Placeholder for CNN logic if needed
        # For now, just use filename as category
        filename = product_image.filename
        category = os.path.splitext(os.path.basename(filename))[0] if filename else ""
        products, response = recommendation_service.recommend_products(category)
        return jsonify({
            "products": products,
            "response": response
        })

@app.route('/')
def home():
    return redirect(url_for('text_query_page'))

@app.route('/text-query', methods=['GET', 'POST'])
def text_query_page():
    response = None
    products = []
    if request.method == 'POST':
        query = request.form.get('query', '')
        if not isinstance(query, str) or len(query) > 256:
            response = "Invalid query."
        else:
            products, response = recommendation_service.recommend_products(query)
    return render_template('text_query.html', products=products, response=response)

@app.route('/ocr-query-page', methods=['GET', 'POST'])
def ocr_query_page():
    response = None
    products = []
    extracted_text = ""
    uploaded_filename = ""
    if request.method == 'POST':
        image_file = request.files.get('image_data')
        if not image_file or not hasattr(image_file, "filename"):
            response = "No image uploaded."
        else:
            extracted_text = ocr_service.extract_text(image_file)
            def is_meaningful(text):
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

@app.route('/product-image-upload', methods=['GET', 'POST'])
def product_image_upload_page():
    response = None
    products = []
    if request.method == 'POST':
        product_image = request.files.get('product_image')
        product_name = request.form.get('product_name', '').strip()
        if not product_image or not hasattr(product_image, "filename"):
            response = "No image uploaded."
        else:
            filename = product_image.filename
            category = os.path.splitext(os.path.basename(filename))[0] if filename else ""
            # Pass with_confidence=True for CNN/Product Image Upload
            products, response = recommendation_service.recommend_products(category, with_confidence=True)
    return render_template('product_image_upload.html', products=products, response=response)

@app.route('/sample_response', methods=['GET'])
def sample_response():
    return render_template('sample_response.html')

app.add_url_rule('/product-recommendation', view_func=ProductRecommendationAPI.as_view('product_recommendation_api'))
app.add_url_rule('/ocr-query', view_func=OCRQueryAPI.as_view('ocr_query_api'))
app.add_url_rule('/image-product-search', view_func=ImageProductSearchAPI.as_view('image_product_search_api'))

@app.route('/product/<product_name>')
def product_detail(product_name):
    # Find the product in the static folder
    import os
    from services.recommendation_service import RecommendationService
    rec_service = RecommendationService()
    static_dir = "static"
    files = os.listdir(static_dir)
    matched_file = None
    # Debug: print product_name and filenames
    print(f"Requested product_name: {product_name}")
    for f in files:
        print(f"Checking file: {f}")
        if product_name.lower() == os.path.splitext(f)[0].replace(" ", "_").lower():
            matched_file = f
            break
    if matched_file:
        # Use the same get_description logic as in RecommendationService
        def get_description(filename):
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
        return render_template('product_detail.html', product=product)
    else:
        return "Product not found", 404

if __name__ == '__main__':
    app.run(debug=True)
