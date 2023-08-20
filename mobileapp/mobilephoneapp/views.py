from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Banner, Product, Like, Rate, User, Comment, Brand
from .paginators import ProductPaginator
from .permissions import CommentOwner
from .serializers import CategorySerializer, BannerSerializer, ProductSerializer, ProductDetailSerializer, \
    CommentSerializer, UserSerializer, CreateCommentSerializer, BrandSerializer


class SampleView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer

    def get_queryset(self):
        q = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            q = q.filter(name__icontains=kw)

        return q


class BrandViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Brand.objects.filter(active=True)
    serializer_class = BrandSerializer

    def get_queryset(self):
        q = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            q = q.filter(name__icontains=kw)

        return q

    @swagger_auto_schema(
        operation_description="Get the product for category product",
        responses={
            status.HTTP_200_OK: ProductSerializer()
        }
    )
    @action(methods=['get'], detail=True, url_path='products')
    def get_products(self, request, pk):
        products = Brand.objects.get(pk=pk).products.filter(active=True)
        kw = request.query_params.get('kw')
        if kw is not None:
            products = products.filter(name__icontains=kw)

        return Response(data=ProductSerializer(products, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductDetailSerializer
    pagination_class = ProductPaginator

    def get_permissions(self):
        if self.action in ['like', 'rating']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = self.queryset
        product = self.request.query_params.get('kw')
        if product is not None:
            queryset = queryset.filter(name__icontains=product)

        brand = self.request.query_params.get('brand')
        if brand is not None:
            queryset = queryset.filter(brand__product=brand)

        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(brand__category=category)

        return queryset

    @action(methods=['get'], detail=True, url_path='comments')
    def get_comments(self, request, pk):
        product = self.get_object()
        comments = product.comments.select_related('user')

        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        product = self.get_object()
        user = request.user

        l, _ = Like.objects.get_or_create(product=product, user=user)
        l.active = not l.active
        l.save()

        return Response(ProductDetailSerializer(l, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='rating')
    def rating(self, request, pk):
        if 'rate' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        product = self.get_object()
        user = request.user

        r, _ = Rate.objects.get_or_create(product=product, user=user)
        r.rate = request.data.get('rate', 0)
        r.save()

        return Response(ProductDetailSerializer(r, context={'request': request}).data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path="current-user")
    def current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView, generics.CreateAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CreateCommentSerializer

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [CommentOwner()]

        return [permissions.IsAuthenticated()]


class BannerViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Banner.objects.filter()
    serializer_class = BannerSerializer
