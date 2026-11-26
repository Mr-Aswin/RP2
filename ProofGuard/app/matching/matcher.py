from rapidfuzz import fuzz
from app.db.database import SessionLocal
from app.db.models import Product, Recall, ProductRecallMatch
from app.schemas import ProductCreate

def normalize_text(value):
    # convert text into a consistent format for comparision
    if not value:
        return ""
    return str(value).strip().lower()

def compare_text(value1,value2):
    # calculate similarity btween 2 text values
    text1 = normalize_text(value1)
    text2 = normalize_text(value2)
    if not text1 or not text2:
        return 0
    # Recognize a short brand name inside a longer manufacturer name
    if text1 == text2:
        return 100
    if len(text1.split()) == 1 and text1 in text2.split():
        return 100
    if len(text2.split()) == 1 and text2 in text1.split():
        return 100
    return fuzz.token_sort_ratio(text1,text2)

def compare_model_numbers(product_model, recall_models):
    # Compare a product model against recall model numbers
    product_model = normalize_text(product_model)
    if not product_model or not recall_models:
        return 0
    best_score = 0
    for recall_model in recall_models:
        recall_model = normalize_text(recall_model)
        if not recall_model:
            continue
        if product_model == recall_model:
            return 100

        # check partial model number matchine
        if min(len(product_model), len(recall_model)) >=4:
            if product_model in recall_model or recall_model in product_model:
                score = 95
            else:
                score = fuzz.ratio(product_model,recall_model)
        else:
            score = fuzz.ratio(product_model,recall_model)
        best_score = max(best_score,score)
    return best_score

def calculate_similarity(product, recall):
    # caculate overall produvt_trall similarity
    brand_score = compare_text(product.brand,recall.manufacturer)
    model_score = compare_model_numbers(product.model_number,recall.model_numbers)
    name_score = compare_text(product.product_name,recall.product_name)

    # weighted similarity score 
    scores = [
        (brand_score,0.4),
        (model_score,0.4),
        (name_score,0.2),
    ]
    available_score = [
        (score,wight)
        for score,wight in scores
        if score > 0
    ]

    if not available_score:
        return 0
    total_weight = sum(weight for __,weight in available_score)
    overall_score = sum(
        score * weight for score, weight in available_score
    )/ total_weight
    return round(overall_score / 100,4)

def match_product_to_recalls(product):
    #  find and save potential recall matches for a product
    db = SessionLocal()
    try:
        recalls = db.query(Recall).all()
        result = []
        for recall in recalls:
            brand_score = compare_text(
                product.brand,
                recall.manufacturer
            )
            model_score = compare_model_numbers(
                product.model_number,
                recall.model_numbers
            )

            name_score = compare_text(
                product.product_name,
                recall.product_name
            )

            # avoide weak or unrelated matches
            if brand_score < 85:
                continue
            if model_score <80 and name_score <90:
                continue
            similarity = calculate_similarity(product, recall)

            # save only when the product alrady existed in the database
            if getattr(product,"id", None) is not None:
                existing_match = db.query(ProductRecallMatch).filter_by(
                    product_id=product.id,
                    recall_id=recall.id
                ).first()

                if not existing_match:
                    new_match = ProductRecallMatch(
                        product_id=product.id,
                        recall_id=recall.id,
                        similarity_score=similarity,
                        match_status="pending_review"
                    )
                    db.add(new_match)
            result.append({
                "recall_id": recall.id,
                "product_name": recall.product_name,
                "manufacturer": recall.manufacturer,
                "model_numbers": recall.model_numbers,
                "similarity_score": similarity,
                "match_status": "pending_review",
                "source_url": recall.source_url
            })
        if getattr(product, "id", None ) is not None:
            db.commit()
        return result
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()