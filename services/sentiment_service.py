"""
Sentiment Analysis Service
Multiple methods from basic to advanced ML
"""

# Method 1: Simple keyword-based (current - no dependencies)
def analyze_sentiment_basic(comment: str, rating: int) -> dict:
    """
    Basic sentiment using rating + simple keywords
    Returns: {'sentiment': 'positive/neutral/negative', 'confidence': 0.0-1.0, 'method': 'basic'}
    """
    # Start with rating-based sentiment
    if rating >= 4:
        base_sentiment = 'positive'
        confidence = 0.7
    elif rating == 3:
        base_sentiment = 'neutral'
        confidence = 0.6
    else:
        base_sentiment = 'negative'
        confidence = 0.7
    
    # Adjust based on comment keywords
    comment_lower = comment.lower()
    
    # Positive keywords
    positive_words = ['amazing', 'excellent', 'great', 'wonderful', 'fantastic', 'love', 
                     'brilliant', 'masterpiece', 'perfect', 'incredible', 'outstanding',
                     'superb', 'awesome', 'best', 'loved', 'enjoyed', 'recommended']
    
    # Negative keywords
    negative_words = ['terrible', 'awful', 'horrible', 'worst', 'bad', 'disappointing',
                     'waste', 'boring', 'poor', 'disappointing', 'hate', 'disappointed',
                     'awful', 'regret', 'skip', 'avoid']
    
    positive_count = sum(1 for word in positive_words if word in comment_lower)
    negative_count = sum(1 for word in negative_words if word in comment_lower)
    
    # Adjust sentiment based on word counts
    if positive_count > negative_count + 2:
        base_sentiment = 'positive'
        confidence = min(0.9, confidence + 0.2)
    elif negative_count > positive_count + 2:
        base_sentiment = 'negative'
        confidence = min(0.9, confidence + 0.2)
    
    return {
        'sentiment': base_sentiment,
        'confidence': confidence,
        'method': 'basic_keywords',
        'positive_words': positive_count,
        'negative_words': negative_count
    }


# Method 2: VADER Sentiment (requires vaderSentiment library)
def analyze_sentiment_vader(comment: str, rating: int) -> dict:
    """
    VADER (Valence Aware Dictionary and sEntiment Reasoner)
    Best for social media text, reviews, short comments
    Install: pip install vaderSentiment
    """
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(comment)
        
        # VADER returns: {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        # compound score: -1 (most negative) to +1 (most positive)
        
        compound = scores['compound']
        
        # Classify based on compound score
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Consider rating too (weighted average)
        rating_sentiment = 'positive' if rating >= 4 else 'neutral' if rating == 3 else 'negative'
        
        # If text and rating disagree significantly, flag it
        disagreement = False
        if (sentiment == 'positive' and rating <= 2) or (sentiment == 'negative' and rating >= 4):
            disagreement = True
        
        return {
            'sentiment': sentiment,
            'confidence': abs(compound),
            'method': 'vader',
            'scores': scores,
            'rating_sentiment': rating_sentiment,
            'disagreement': disagreement
        }
        
    except ImportError:
        # Fall back to basic if VADER not installed
        return analyze_sentiment_basic(comment, rating)


# Method 3: TextBlob (requires textblob library)
def analyze_sentiment_textblob(comment: str, rating: int) -> dict:
    """
    TextBlob sentiment analysis
    Good for general text, easier to use than VADER
    Install: pip install textblob
    """
    try:
        from textblob import TextBlob
        
        blob = TextBlob(comment)
        
        # Polarity: -1 (negative) to +1 (positive)
        # Subjectivity: 0 (objective) to 1 (subjective)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': abs(polarity),
            'method': 'textblob',
            'polarity': polarity,
            'subjectivity': subjectivity
        }
        
    except ImportError:
        return analyze_sentiment_basic(comment, rating)


# Method 4: Hugging Face Transformers (Advanced ML)
def analyze_sentiment_transformers(comment: str, rating: int) -> dict:
    """
    Advanced ML using pre-trained transformer models
    Most accurate but requires more resources
    Install: pip install transformers torch
    
    NOTE: This is heavy! Use only on EC2 with GPU, not locally
    """
    try:
        from transformers import pipeline
        
        # Load pre-trained sentiment analysis model
        # This downloads ~500MB model on first run!
        classifier = pipeline('sentiment-analysis', 
                            model='distilbert-base-uncased-finetuned-sst-2-english')
        
        result = classifier(comment)[0]
        
        # Result: {'label': 'POSITIVE' or 'NEGATIVE', 'score': confidence}
        
        sentiment = result['label'].lower()
        confidence = result['score']
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'method': 'transformers_distilbert',
            'model': 'distilbert-base-uncased-finetuned-sst-2-english'
        }
        
    except Exception as e:
        print(f"Transformers error: {e}")
        return analyze_sentiment_vader(comment, rating)


# Method 5: AWS Comprehend (Cloud-based, for production)
def analyze_sentiment_aws_comprehend(comment: str, rating: int) -> dict:
    """
    AWS Comprehend - Cloud-based sentiment analysis
    Best for production, no local ML models needed
    Requires: boto3 and AWS credentials
    Cost: $0.0001 per request (very cheap!)
    """
    try:
        import boto3
        
        comprehend = boto3.client('comprehend', region_name='us-east-1')
        
        response = comprehend.detect_sentiment(
            Text=comment,
            LanguageCode='en'
        )
        
        # Response includes: POSITIVE, NEGATIVE, NEUTRAL, MIXED
        # Plus confidence scores for each
        
        sentiment = response['Sentiment'].lower()
        scores = response['SentimentScore']
        
        # Get confidence for detected sentiment
        confidence_map = {
            'positive': scores['Positive'],
            'negative': scores['Negative'],
            'neutral': scores['Neutral'],
            'mixed': scores['Mixed']
        }
        
        confidence = confidence_map.get(sentiment, 0.5)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'method': 'aws_comprehend',
            'scores': scores
        }
        
    except Exception as e:
        print(f"AWS Comprehend error: {e}")
        return analyze_sentiment_vader(comment, rating)


# Main function - automatically selects best available method
def analyze_sentiment(comment: str, rating: int, method: str = 'auto') -> dict:
    """
    Main sentiment analysis function
    
    Args:
        comment: User's review text
        rating: Star rating (1-5)
        method: 'auto', 'basic', 'vader', 'textblob', 'transformers', 'aws'
    
    Returns:
        {
            'sentiment': 'positive/negative/neutral/mixed',
            'confidence': 0.0-1.0,
            'method': 'method_used',
            ... additional fields based on method
        }
    """
    if method == 'auto':
        # Try methods in order of preference
        # For production: AWS Comprehend > VADER > TextBlob > Basic
        # For development: VADER > TextBlob > Basic
        
        try:
            # Try VADER first (best balance of accuracy and speed)
            return analyze_sentiment_vader(comment, rating)
        except:
            try:
                # Fall back to TextBlob
                return analyze_sentiment_textblob(comment, rating)
            except:
                # Last resort: basic keywords
                return analyze_sentiment_basic(comment, rating)
    
    elif method == 'basic':
        return analyze_sentiment_basic(comment, rating)
    
    elif method == 'vader':
        return analyze_sentiment_vader(comment, rating)
    
    elif method == 'textblob':
        return analyze_sentiment_textblob(comment, rating)
    
    elif method == 'transformers':
        return analyze_sentiment_transformers(comment, rating)
    
    elif method == 'aws':
        return analyze_sentiment_aws_comprehend(comment, rating)
    
    else:
        return analyze_sentiment_basic(comment, rating)


# Batch analysis for analytics
def analyze_all_feedback(feedbacks: list) -> dict:
    """
    Analyze sentiment distribution across all feedback
    
    Args:
        feedbacks: List of feedback dicts with 'comment' and 'rating'
    
    Returns:
        {
            'total': int,
            'positive': int,
            'negative': int,
            'neutral': int,
            'average_confidence': float,
            'sentiment_distribution': {...}
        }
    """
    results = {
        'total': len(feedbacks),
        'positive': 0,
        'negative': 0,
        'neutral': 0,
        'mixed': 0,
        'total_confidence': 0
    }
    
    for feedback in feedbacks:
        analysis = analyze_sentiment(feedback.get('comment', ''), 
                                    feedback.get('rating', 3))
        
        sentiment = analysis['sentiment']
        results[sentiment] = results.get(sentiment, 0) + 1
        results['total_confidence'] += analysis['confidence']
    
    if results['total'] > 0:
        results['average_confidence'] = results['total_confidence'] / results['total']
    else:
        results['average_confidence'] = 0
    
    # Calculate percentages
    results['sentiment_distribution'] = {
        'positive': (results['positive'] / results['total'] * 100) if results['total'] > 0 else 0,
        'negative': (results['negative'] / results['total'] * 100) if results['total'] > 0 else 0,
        'neutral': (results['neutral'] / results['total'] * 100) if results['total'] > 0 else 0,
        'mixed': (results.get('mixed', 0) / results['total'] * 100) if results['total'] > 0 else 0
    }
    
    return results