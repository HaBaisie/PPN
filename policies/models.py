from django.db import models
from django.conf import settings


class Policy(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'policymaker'})
    created_at = models.DateTimeField(auto_now_add=True)

    def get_ai_insights(self):
        comments = self.comment_set.all()
        if not comments.exists():
            return {"sentiment": "Neutral", "recommendation": "No data yet."}

        positive_words = ['good', 'positive', 'support', 'great', 'benefit', 'useful']
        negative_words = ['bad', 'negative', 'oppose', 'poor', 'harm', 'concern']
        scores = []
        for c in comments:
            text = (c.text or '').lower()
            score = 0
            if any(w in text for w in positive_words):
                score = 1
            elif any(w in text for w in negative_words):
                score = -1
            scores.append(score)
        avg_sentiment = sum(scores) / len(scores)
        sentiment = "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"

        likes_count = self.like_set.count()
        reshares_count = self.reshare_set.count()
        popularity = likes_count + reshares_count

        recommendation = f"Sentiment: {sentiment}. Popularity: {popularity}. " + ("Expand if positive." if avg_sentiment > 0 else "Review if negative.")
        return {"sentiment": sentiment, "recommendation": recommendation}


class Comment(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('policy', 'user')


class Reshare(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('policy', 'user')


class ChatMessage(models.Model):
    """Simple chat messages for a dashboard chat box."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"
