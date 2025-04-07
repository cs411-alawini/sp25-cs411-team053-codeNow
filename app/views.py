from django.shortcuts import render


from rest_framework import generics
from .models import Skill
from .serializers import SkillSerializer

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
