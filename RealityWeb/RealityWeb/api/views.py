# from rest_framework.generics import GenericAPIView
# from rest_framework import mixins
from rest_framework.decorators import api_view
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from django.http import JsonResponse
from django.contrib import messages

import pandas as pd
import pickle

from ..models import GetPriceModel
from .serializers import GetPriceSerializer



class GetPriceApiModel(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = GetPriceModel.objects.all()
    serializer_class = GetPriceSerializer
    lookup_field = "id"

    def get(self, request, id=None):
        if id:
            return self.retrieve(request)

        else:
            return self.list(request)

    def post(self, request):
        return self.create(request)

    def delete(self, request, id):
        return self.destroy(request, id)

@api_view(["POST"])
def getprice(request):
    try:
        myData = request.data
        df = pd.DataFrame(myData, index=[0])
        print(table_preparation())
        messages.success(request, table_preparation())
        return JsonResponse(myData, safe=False)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

def table_preparation():
    file = open('RealityWeb/api/col_model_warszawa.sav', 'rb')
    pickle_loaded = pickle.load(file)
    #df_pickle = pd.read_pickle('RealityWeb/api/finalized_model_warszawa.sav')
    print(pickle_loaded)



