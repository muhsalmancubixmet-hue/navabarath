# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import HeroSection, HonorableCertificate, Testimonial, Campaign, Category, CampaignImage

class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']

class CampaignImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignImage
        fields = ['id', 'image']

class CampaignSerializer(serializers.ModelSerializer):
    primary_category_details = CategorySerializer(source='primary_category', read_only=True)
    secondary_category_details = CategorySerializer(source='secondary_category', read_only=True)
    images = CampaignImageSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    primary_category_details = CategorySerializer(source='primary_category', read_only=True)
    secondary_category_details = CategorySerializer(source='secondary_category', read_only=True)

    class Meta:
        model = HonorableCertificate
        fields = '__all__'