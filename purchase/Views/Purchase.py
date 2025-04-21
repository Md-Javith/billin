from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from purchase.serializers import PurchaseOrderSerializer

class CreatePurchaseOrderAPIView(APIView):
    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            purchase_order = serializer.save()
            return Response({'message': 'Purchase Order created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


















































# from rest_framework import generics, permissions
# from purchase.seriaizers import PurchaseOrderSerializer

# class PurchaseOrderCreateView(generics.CreateAPIView):
#     serializer_class = PurchaseOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
