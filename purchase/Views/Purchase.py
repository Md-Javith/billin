from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from purchase.serializers import PurchaseOrderSerializer
from rest_framework import serializers, generics, status


class CreatePurchaseOrderAPIView(generics.CreateAPIView):
    """
    POST /api/purchase-orders/
    """
    serializer_class = PurchaseOrderSerializer

    def create(self, request, *args, **kwargs):
        """
        Override to return a simple success message.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Purchase Order created successfully"},
            status=status.HTTP_201_CREATED
        )










































# from rest_framework import generics, permissions
# from purchase.seriaizers import PurchaseOrderSerializer

# class PurchaseOrderCreateView(generics.CreateAPIView):
#     serializer_class = PurchaseOrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
