from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from django.core.exceptions import ObjectDoesNotExist as DoesNotExists
from .serializers import UsersSerializer
from .serializers import LocationPutSerializer
from .serializers import LocationGetSerializer
from .serializers import GpsRoutePutSerializer
from .serializers import GpsRouteGetSerializer
from .serializers import changeMakeSerializer # test
from .serializers import NewRoutePutSerializer
from .serializers import NewRouteGetSerializer
from .serializers import JaywalkingPostSerializer
from .serializers import JaywalkingGetSerializer
from .serializers import VoiceFileUploadSerializer
#from .serializers import SafeZoneSerializer
from .models import Users
from .models import Location
from .models import GpsRoute
from .models import NewRoute
from .models import Jaywalking
from .models import VoiceFile
#from .models import SafeZone
from datetime import datetime
from shapely.geometry import Point, LineString
import geopandas as gpd
import os
import logging
import json


# Get an instance of a logger
logger = logging.getLogger('django.request')

# Create your views here.


@csrf_exempt
def users_list(request):
    if request.method == 'GET':
        query_set = Users.objects.all()
        serializer = UsersSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UsersSerializer(data=data) 
        if serializer.is_valid():
            serializer.save()
            try:
                Location.objects.get(pk=data['smartBadgeID'])
            except DoesNotExists:
                Location.objects.create(smartBadgeID=data['smartBadgeID'])
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)



@csrf_exempt
def users(request, pk):
    
    obj = Users.objects.get(pk=pk)

    if request.method == 'GET':
        serializer = UsersSerializer(obj)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UsersSerializer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        obj.delete()
        return HttpResponse(status=204)



@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        search_name = data['smartBadgeID']
        obj = Users.objects.get(smartBadgeID=search_name)

        if data['userID'] == obj.userID:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400) 



def getPoint(gpsQueryData):
    longitude = gpsQueryData.get("longitude")
    latitude = gpsQueryData.get("latitude")
    return Point(longitude, latitude)

@csrf_exempt
def changeMakeState(request, pk):
    obj = Location.objects.get(pk=pk)
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = changeMakeSerializer(obj, data=data)

        if data['makeNewZoneState']:
            new_set = obj.newRoute.all()
            newZoneSerializer = GpsRoutePutSerializer(new_set, many=True)
            for i in newZoneSerializer.data:
                GpsRoute.objects.create(
                    smartBadge=obj,
                    longitude=i['longitude'],
                    latitude=i['latitude'],
                    updated_at=datetime.now
                    )
            new_set.delete()
                    
        if data['makeState']:
            query_set = obj.smartBadge.all()
            logger.debug(query_set)
            routeSerializer = GpsRoutePutSerializer(query_set, many=True)
            temp_list = (list(map(lambda x: getPoint(x), routeSerializer.data)))
            store_list = temp_list[:]
            for i in range(len(temp_list)):
                for j in range(i+1, len(temp_list)):
                    if temp_list[i].distance(temp_list[j]) < 0.0001:
                        store_list.remove(temp_list[i])
                        break
        
            query_set.delete()

            for i in store_list:
                GpsRoute.objects.create(
                    smartBadge=obj, 
                    longitude=i.x, 
                    latitude=i.y,
                    updated_at=datetime.now
                )


        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.data, status=400)  


@csrf_exempt
def location(request, pk):
    
    obj = Location.objects.get(pk=pk)
    # location GET
    if request.method == 'GET':
        serializer = LocationGetSerializer(obj)
        return JsonResponse(serializer.data, safe=False)
    # location PUT
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = LocationPutSerializer(obj, data=data)
        routeSerializer = GpsRoutePutSerializer(data=data)
        maked = obj.makeState
        nextPoint = Point([float(data['longitude']), float(data['latitude'])])
        
        # out 10m and not maked safeZone : Save gps to gpsRoute
        if obj.smartBadge.exists():
            query_set = obj.smartBadge.latest('id')
            if routeSerializer.is_valid() and not maked:
                prePoint = Point([query_set.longitude, query_set.latitude])            
                if not prePoint.buffer(0.0001).contains(nextPoint):
                    logger.debug("save routeSerializer, not maked")
                    routeSerializer.save(smartBadge=obj, updated_at=datetime.now)
                else:
                    logger.debug("not save routeSerializer, not maked")
        else:
            logger.debug("does not exists")
            if routeSerializer.is_valid():
                routeSerializer.save(smartBadge=obj, updated_at=datetime.now)
#        query_set = obj.smartBadge.latest('id')
#        if routeSerializer.is_valid() and not maked:
#            prePoint = Point([query_set.longitude, query_set.latitude])            
#            if not prePoint.buffer(0.0001).contains(nextPoint):
#                logger.debug("save routeSerializer, not maked")
#                routeSerializer.save(smartBadge=obj, updated_at=datetime.now)
#            else:
#                logger.debug("not save routeSerializer, not maked")

        # SafeZone maked True : check safeState, save safeState
        if serializer.is_valid() and maked:
            query_set = obj.smartBadge.all()
            zoneSerializer = GpsRouteGetSerializer(query_set, many=True)
            safeZone = gpd.GeoSeries(LineString(list(map(lambda x: getPoint(x), zoneSerializer.data))))
            checkPoint = gpd.GeoSeries(nextPoint.buffer(0.0001))
            flag = safeZone.intersects(checkPoint)[0]

            if flag:
                serializer.save(safeState=True, updated_at=datetime.now)
                logger.debug("save location, maked, safeState=True")
            else:
                serializer.save(safeState=False, updated_at=datetime.now)
                logger.debug("save location, maked, safeState=False")
                
                # save Location to newRoute
                newRouteSerializer = NewRoutePutSerializer(data=data)
                if newRouteSerializer.is_valid():
                    if obj.newRoute.exists():
                        new_set = obj.newRoute.latest("id")
                        prePoint = Point([new_set.longitude, new_set.latitude])
                        if not prePoint.buffer(0.0001).contains(nextPoint):
                            newRouteSerializer.save(smartBadge=obj, updated_at=datetime.now)
                    else:
                        newRouteSerializer.save(smartBadge=obj, updated_at=datetime.now)

            return JsonResponse(serializer.data, status=201)

        elif serializer.is_valid() and not maked:
            serializer.save(safeState=True, updated_at=datetime.now)
            logger.debug("save location, not maked")
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.data, status=400)
    # location DELETE
    elif request.method == 'DELETE':
        obj.delete()
        return HttpResponse(status=204)

    else:
        return HttpResponse(status=400)



@csrf_exempt
def gps_route(request, pk):
    
    smartBadgeObj = Location.objects.get(pk=pk)

    if request.method == 'GET':
        query_set = smartBadgeObj.smartBadge.all()
        serializer = GpsRouteGetSerializer(query_set, many=True)
         
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'DELETE':
        objAll = smartBadgeObj.smartBadge.latest('id')
        objAll.delete()
        return HttpResponse(status=204)


@csrf_exempt
def new_route(request, pk):

    smartBadgeObj = Location.objects.get(pk=pk)

    if request.method == 'GET':
        query_set = smartBadgeObj.newRoute.all()
        serializer = NewRouteGetSerializer(query_set, many=True)

        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'DELETE':
        objAll = smartBadgeObj.newRoute.all()
        objAll.delete()
        return HttpResponse(status=204)


@csrf_exempt
def jaywalking(request, pk):
    obj = Location.objects.get(pk=pk)

    if request.method == 'GET':
        query_set = obj.jaywalking.all()
        serializer = JaywalkingGetSerializer(query_set, many=True)

        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        longitude = obj.longitude
        latitude = obj.latitude
        Jaywalking.objects.create(smartBadge=obj, longitude=longitude, latitude=latitude, updated_at=datetime.now)

        return HttpResponse(status=200)

    elif request.method == 'DELETE':
        objAll = obj.jaywalking.all()
        objAll.delete()

        return HttpResponse(status=204)


class VoiceFileUploadViewSet(viewsets.ModelViewSet):
    queryset = VoiceFile.objects.all()
    serializer_class = VoiceFileUploadSerializer

    @action(detail=True, methods=['get'])
    def voiceFile(self, request, pk=None):
        r = self.get_object()
        ext = '*'
        if r.voiceFile.path:
            ext = r.voiceFile.path.split('.')[-1]
        content_type = 'audio/' + ext
        
        response = FileResponse(open(r.voiceFile.path, 'rb'), content_type=content_type) 
        return response

#    @action(detail=False, methods=['put'])
#    def uploads(self, request):
#        smartBadgeID = request.data['smartBadgeID']
#        title = request.data['title']

#    def get_queryset(self):
#        query_smartBadgeID = self.request.data['smartBadgeID']
#        query_title = self.request.data['title']
#        return VoiceFile.objects.filter(smartBadgeID=query_smartBadgeID, title=query_title)


#@csrf_exempt
#def safe_zone(request, pk):

#    smartBadgeObj = Location.objects.get(pk=pk)

#    if request.method == 'POST':
#        test_s = LineString(gpd.GeoSeries([Point(127.1750, 36.8331), 
#        Point(127.1752, 36.8332), Point(127.1753, 36.8335)]))

#        SafeZone.objects.create(smartBadge=smartBadgeObj, zone=test_s)
#        logger.debug(test_s)
#        return HttpResponse(status=200)

