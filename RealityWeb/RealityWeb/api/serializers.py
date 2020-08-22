from rest_framework.serializers import ModelSerializer

from ..models import GetPriceModel

class GetPriceSerializer(ModelSerializer):
    class Meta:
        model = GetPriceModel
        fields = '__all__'
