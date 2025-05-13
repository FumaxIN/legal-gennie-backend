from rest_framework import serializers
from typing import Dict, Any, List

class CaseCreateSerializer(serializers.Serializer):
    petition = serializers.CharField()
    token = serializers.CharField(required=False, help_text="Indian Kanoon API token")

class JudgmentSerializer(serializers.Serializer):
    tid = serializers.IntegerField()
    title = serializers.CharField()
    doctype = serializers.IntegerField(required=False)
    publishdate = serializers.CharField(required=False)
    docsource = serializers.CharField(required=False)
    citation = serializers.CharField(required=False)
    headline = serializers.CharField(required=False)

class CaseResponseSerializer(serializers.Serializer):
    prediction = serializers.CharField()
    search_query = serializers.CharField()
    judgments = JudgmentSerializer(many=True, required=False)
