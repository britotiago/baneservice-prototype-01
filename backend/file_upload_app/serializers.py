from rest_framework import serializers
from .models import Category, AssessmentIssue, AssessmentCriteria

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AssessmentIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentIssue
        fields = '__all__'

class AssessmentCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentCriteria
        fields = '__all__'
