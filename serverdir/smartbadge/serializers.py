from smartbadge.models import Users
from smartbadge.models import Location
from smartbadge.models import GpsRoute
from smartbadge.models import NewRoute
from smartbadge.models import Jaywalking
from smartbadge.models import VoiceFile
#from smartbadge.models import SafeZone
from rest_framework import serializers


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('smartBadgeID', 'userID')

class changeMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('smartBadgeID', 'makeState')

class LocationPutSerializer(serializers.ModelSerializer):
    # updated_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    class Meta:
        model = Location
        fields = ('smartBadgeID', 'longitude', 'latitude')

class LocationGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('smartBadgeID', 'longitude', 'latitude', 'safeState', 'makeState', 'updated_at')


class GpsRoutePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = GpsRoute
        fields = ('longitude', 'latitude')

class GpsRouteGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GpsRoute
        fields = ('longitude', 'latitude', 'updated_at')


class NewRoutePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewRoute
        fields = ('longitude', 'latitude')

class NewRouteGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewRoute
        fields = ('longitude', 'latitude', 'updated_at')

class JaywalkingPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jaywalking
        fields = ('smartBadge')

class JaywalkingGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jaywalking
        fields = ('longitude', 'latitude', 'updated_at')

class VoiceFileUploadSerializer(serializers.HyperlinkedModelSerializer):
    voiceFile_url = serializers.HyperlinkedIdentityField(view_name='voicefile-voiceFile', read_only=True)
    class Meta:
        model = VoiceFile
        fields = ('url', 'pk', 'smartBadgeID', 'title', 'voiceFile', 'voiceFile_url')

#class SafeZoneSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = SafeZone
#        fields = ('smartBadge', 'zone')
