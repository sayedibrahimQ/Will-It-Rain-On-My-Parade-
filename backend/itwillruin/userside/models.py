from django.db import models


class History(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    forecast_prediction = models.JSONField()
    ai_insights = models.JSONField()
    date = models.DateField()
    event = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    