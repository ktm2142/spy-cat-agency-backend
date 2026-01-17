import requests
from rest_framework import serializers
from .models import Cat, Mission, Target


class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = ["id", "name", "years_of_experience", "breed", "salary"]

    def validate_breed(self, value):
        try:
            response = requests.get("https://api.thecatapi.com/v1/breeds")
            if response.status_code == 200:
                breeds = response.json()
                valid_breeds = [breed["name"] for breed in breeds]
                if value not in valid_breeds:
                    raise serializers.ValidationError(
                        f"Breed '{value}' is not valid. Please choose from valid cat breeds {valid_breeds}"
                    )
            else:
                raise serializers.ValidationError("Unable to validate breed. TheCatAPI is unavailable.")
        except requests.exceptions.RequestException:
            raise serializers.ValidationError("Unable to validate breed. Connection error.")
        return value


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ["id", "name", "country", "notes", "complete"]
        read_only_fields = ["id"]


class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)

    class Meta:
        model = Mission
        fields = ["id", "cat", "complete", "targets"]
        read_only_fields = ["id", "complete"]

    def validate_targets(self, value):
        if not (1 <= len(value) <= 3):
            raise serializers.ValidationError("Mission must have between 1 and 3 targets.")

        seen = set()
        for t in value:
            key = (t.get("name"), t.get("country"))
            if key in seen:
                raise serializers.ValidationError("Targets must be unique within a mission (name+country).")
            seen.add(key)
        return value

    def create(self, validated_data):
        targets_data = validated_data.pop("targets")
        mission = Mission.objects.create(**validated_data)

        Target.objects.bulk_create(
            [Target(mission=mission, **t) for t in targets_data]
        )
        return mission
