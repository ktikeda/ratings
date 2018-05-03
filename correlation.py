"""Pearson correlation."""

from math import sqrt
from flask_sqlalchemy import SQLAlchemy


def pearson(pairs):
    """Return Pearson correlation for pairs.
    Using a set of pairwise ratings, produces a Pearson similarity rating.
    """

    series_1 = [float(pair[0]) for pair in pairs]
    series_2 = [float(pair[1]) for pair in pairs]

    sum_1 = sum(series_1)
    sum_2 = sum(series_2)

    squares_1 = sum([n * n for n in series_1])
    squares_2 = sum([n * n for n in series_2])

    product_sum = sum([n * m for n, m in pairs])

    size = len(pairs)

    numerator = product_sum - ((sum_1 * sum_2) / size)

    denominator = sqrt(
        (squares_1 - (sum_1 * sum_1) / size) *
        (squares_2 - (sum_2 * sum_2) / size)
    )

    if denominator == 0:
        return 0

    return numerator / denominator

m = Movie.query.filter_by(title="Toy Story").one()
u = User.query.get(1)    # someone we know who hasn't rated TS

ratings = u.ratings # User 1's ratings in a list of Rating objects
user1_movies = set([r.movie for r in ratings])

# Find users who have also rated Toy Story
other_ratings = Rating.query.filter_by(movie_id=m.movie_id).all()
other_users = [r.user for r in other_ratings]

pearson_nums = {}

for user in other_users:
    pairs = []
    user_movies = set([r.movie for r in user.ratings])
    common_movies = user1_movies && user_movies
    
    for movie in common_movies:
        rating1 = Rating.query.filter(
            Rating.movie_id == movie.movie_id, Rating.user_id == u.user_id).one()
        rating2 = Rating.query.filter(
            Rating.movie_id == movie.movie_id, Rating.user_id == user.user_id).one()
        pairs.append((int(rating1.score), int(rating2.score)))

    pearson_num = pearson(pairs)

    if len(pairs) > 4 or pearson_num > 0.95:
        pearson_nums[user] = pearson_num
    
