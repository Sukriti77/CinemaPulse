from database.dynamodb_db import DynamoDBDatabase
from config import get_config
from datetime import datetime

config = get_config()

db = DynamoDBDatabase(
    region_name=config.AWS_REGION,
    users_table=config.DYNAMODB_USERS_TABLE,
    movies_table=config.DYNAMODB_MOVIES_TABLE,
    feedback_table=config.DYNAMODB_FEEDBACK_TABLE
)

movies = [
    {
        "movie_id": 1,  # ✅ NUMBER, NOT STRING
        "title": "Inception",
        "description": "A thief who steals corporate secrets through dream-sharing technology.",
        "genre": "Sci-Fi",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/7/7f/Inception_ver3.jpg",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "movie_id": 2,
        "title": "Interstellar",
        "description": "A team of explorers travel through a wormhole in space.",
        "genre": "Sci-Fi",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
        "created_at": datetime.utcnow().isoformat()
    },
    {
        "movie_id": 3,
        "title": "The Dark Knight",
        "description": "Batman faces the Joker in Gotham City.",
        "genre": "Action",
        "poster_url": "https://upload.wikimedia.org/wikipedia/en/8/8a/Dark_Knight.jpg",
        "created_at": datetime.utcnow().isoformat()
    }
]

for movie in movies:
    try:
        db.movies_table.put_item(
            Item=movie,
            ConditionExpression="attribute_not_exists(movie_id)"
        )
        print(f"✅ Added movie: {movie['title']}")
    except Exception as e:
        print(f"⚠️ Movie already exists: {movie['title']} | {e}")

print("🎉 Movies seeded successfully")
