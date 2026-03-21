import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from surprise import SVD, Dataset, Reader
import pandas as pd


COMMENT_SERVICE_URL = "http://comment-rate-service:8000/ratings/"
TOP_N = 10  # number of recommendations to return


def fetch_all_ratings():
    """Fetch all ratings from comment-rate-service, handling pagination."""
    results = []
    url = COMMENT_SERVICE_URL
    while url:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            # DRF list: could be paginated ({"results": [...], "next": ...}) or a plain list
            if isinstance(data, list):
                results.extend(data)
                break
            else:
                results.extend(data.get("results", []))
                url = data.get("next")  # None ends the loop
        except Exception as e:
            raise RuntimeError(f"Cannot reach comment-rate-service: {e}")
    return results


@api_view(["GET"])
def recommend(request, user_id):
    """
    GET /api/recommend/<user_id>/
    Returns a list of recommended book IDs for the given user using SVD.
    """
    try:
        ratings_data = fetch_all_ratings()
    except RuntimeError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if len(ratings_data) < 2:
        return Response(
            {
                "user_id": user_id,
                "recommended_book_ids": [],
                "message": "Chưa có đủ dữ liệu để gợi ý sách.",
            }
        )

    # Build DataFrame
    df = pd.DataFrame(ratings_data)
    # Ensure expected columns exist
    required_cols = {"user_id", "book_id", "rating"}
    if not required_cols.issubset(df.columns):
        return Response(
            {"error": "Dữ liệu từ Comment Service không đúng định dạng."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    df = df[["user_id", "book_id", "rating"]].dropna()
    df["user_id"] = df["user_id"].astype(int)
    df["book_id"] = df["book_id"].astype(int)
    df["rating"] = df["rating"].astype(float)

    # Check if user exists in the dataset
    user_exists = user_id in df["user_id"].values

    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(df[["user_id", "book_id", "rating"]], reader)
    trainset = dataset.build_full_trainset()

    # Train SVD
    algo = SVD(n_factors=50, n_epochs=20, random_state=42)
    algo.fit(trainset)

    # All unique book IDs
    all_book_ids = df["book_id"].unique().tolist()

    # Books already rated by this user
    if user_exists:
        rated_books = set(df[df["user_id"] == user_id]["book_id"].tolist())
    else:
        rated_books = set()

    # Predict rating for each unrated book
    candidates = [bid for bid in all_book_ids if bid not in rated_books]

    if not candidates:
        return Response(
            {
                "user_id": user_id,
                "recommended_book_ids": [],
                "message": "Bạn đã đánh giá tất cả sách hiện có.",
            }
        )

    predictions = []
    for book_id in candidates:
        pred = algo.predict(user_id, book_id)
        predictions.append((book_id, pred.est))

    # Sort by predicted rating descending
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_book_ids = [int(bid) for bid, _ in predictions[:TOP_N]]

    return Response(
        {
            "user_id": user_id,
            "recommended_book_ids": top_book_ids,
        }
    )
