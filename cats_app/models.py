from django.db import models


class Cat(models.Model):
    name = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField(default=0)
    salary = models.PositiveIntegerField(default=0)


class Mission(models.Model):
    cat = models.ForeignKey(Cat, null=True, blank=True, on_delete=models.SET_NULL, related_name='missions')
    complete = models.BooleanField(default=False)


class Target(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='targets')
    name = models.CharField(max_length=140)
    country = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    complete = models.BooleanField(default=False)
