#from django.db import models

# Create your models here.
from django.db import models
#from django.contrib.gis.db import models

class Users(models.Model):
    smartBadgeID = models.IntegerField(primary_key=True)
    userID = models.IntegerField()

    class Meta:
        ordering = ['smartBadgeID']
    
    def __str__(self):
        return self.smartBadgeID


class Location(models.Model):
   # user = models.OneToOneField(
   #     Users,
   #     on_delete = models.CASCADE,
   #     primary_key=True,
   # )
    smartBadgeID = models.IntegerField(primary_key=True, default=0)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    safeState = models.BooleanField(default=True)
    makeState = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True)

    class Meta:
        ordering = ['smartBadgeID']

    def __str__(self):
        return self.longitude + " : " + self.latitude


class GpsRoute(models.Model):
    smartBadge = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='smartBadge')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True)

    class Meta:
        ordering = ['smartBadge']
    def __str__(self):
        return self.longitude + " : " + self.latitude


class NewRoute(models.Model): 
    smartBadge = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='newRoute')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True)
    class Meta:
        ordering = ['smartBadge']
    def __str__(self):
        return self.longitude + " : " + self.latitude


class Jaywalking(models.Model):
    smartBadge = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='jaywalking')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True, editable=False, null=True)


class VoiceFile(models.Model):
    #smartBadge = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='voiceFile')
    smartBadgeID = models.IntegerField(default=1)
    title = models.CharField(max_length=100)
    voiceFile = models.FileField(null=True)

    #class Meta:
    #    ordering = ['smartBadge']
    



#Use Geodjango 
#class SafeZone(models.Model):
#    smartBadge = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='smartBadge')
#    zone = models.LineStringField()

#    class Meta:
#        ordering = ['smartBadge']
#    def __str__(self):
#        return "This Field return LineString zone"
