from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cat, Mission, Target
from .serializers import CatSerializer, MissionSerializer


class CatViewSet(viewsets.ModelViewSet):
    serializer_class = CatSerializer
    queryset = Cat.objects.all()

    def partial_update(self, request, *args, **kwargs):
        allowed_fields = {"salary"}
        request_fields = set(request.data.keys())

        if not request_fields.issubset(allowed_fields):
            return Response(
                {"error": "Only 'salary' field can be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)


class MissionViewSet(viewsets.ModelViewSet):
    serializer_class = MissionSerializer
    queryset = Mission.objects.prefetch_related("targets").select_related("cat").all()

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()
        if mission.cat_id is not None:
            return Response(
                {"error": "Mission cannot be deleted because it is assigned to a cat."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        mission = self.get_object()

        if mission.cat_id is not None:
            return Response(
                {"error": "Mission is already assigned to a cat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cat_id = request.data.get("cat_id")
        if not cat_id:
            return Response({"error": "cat_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cat = Cat.objects.get(pk=cat_id)
        except Cat.DoesNotExist:
            return Response({"error": "Cat not found."}, status=status.HTTP_404_NOT_FOUND)

        if Mission.objects.filter(cat=cat, complete=False).exists():
            return Response(
                {"error": "This cat already has an active mission."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if mission.complete:
            return Response(
                {"error": "Cannot assign a cat to a completed mission."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mission.cat = cat
        mission.save(update_fields=["cat"])
        return Response(self.get_serializer(mission).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path=r"targets/(?P<target_id>[^/.]+)")
    def update_target(self, request, pk=None, target_id=None):
        mission = self.get_object()

        try:
            target = mission.targets.get(pk=target_id)
        except Target.DoesNotExist:
            return Response({"error": "Target not found in this mission."}, status=status.HTTP_404_NOT_FOUND)

        if mission.complete:
            return Response({"error": "Mission is completed. Targets are frozen."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data

        if "notes" in data:
            if target.complete:
                return Response({"error": "Target is completed. Notes are frozen."}, status=status.HTTP_400_BAD_REQUEST)
            target.notes = data["notes"]

        if "complete" in data:
            if data["complete"] is True and not target.complete:
                target.complete = True
            elif data["complete"] is False:
                return Response({"error": "You cannot un-complete a target."}, status=status.HTTP_400_BAD_REQUEST)

        target.save()

        if not mission.complete and not mission.targets.filter(complete=False).exists():
            mission.complete = True
            mission.save(update_fields=["complete"])

        return Response(self.get_serializer(mission).data, status=status.HTTP_200_OK)
