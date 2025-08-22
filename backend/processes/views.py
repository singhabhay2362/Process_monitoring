from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from django.db import models
import logging

from .models import Process, SystemInfo
from .serializers import ProcessSerializer, SystemInfoSerializer

logger = logging.getLogger(__name__)


class ProcessViewSet(viewsets.ModelViewSet):
    serializer_class = ProcessSerializer

    def get_queryset(self):
        # Return only the latest processes (e.g., last 10 seconds)
        time_threshold = timezone.now() - timedelta(seconds=10)
        return Process.objects.filter(timestamp__gte=time_threshold).order_by('-timestamp')

    def create(self, request, *args, **kwargs):
        try:
            if isinstance(request.data, list):
                logger.info(f"Received {len(request.data)} process records")
                serializer = self.get_serializer(data=request.data, many=True)
            else:
                logger.info("Received single process record")
                serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info("Process data saved successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error saving process data: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ New endpoint: /api/processes/host/<hostname>/
    @action(detail=False, methods=["get"], url_path="host/(?P<hostname>[^/.]+)")
    def host_details(self, request, hostname=None):
        try:
            processes = Process.objects.filter(hostname=hostname)
            if not processes.exists():
                return Response({"error": f"No processes found for host {hostname}"}, status=status.HTTP_404_NOT_FOUND)

            # Stats
            total_processes = processes.count()
            avg_cpu = processes.aggregate(avg_cpu=models.Avg("cpu_percent"))["avg_cpu"] or 0
            avg_memory = processes.aggregate(avg_memory=models.Avg("memory_usage"))["avg_memory"] or 0
            avg_disk = processes.aggregate(avg_disk=models.Avg("disk_usage"))["avg_disk"] or 0
            avg_net = processes.aggregate(avg_net=models.Avg("net_usage"))["avg_net"] or 0
            latest_timestamp = processes.order_by("-timestamp").first().timestamp

            details = {
                "hostname": hostname,
                "total_processes": total_processes,
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory,
                "avg_disk": avg_disk,
                "avg_net": avg_net,
                "latest_timestamp": latest_timestamp,
            }
            return Response(details, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching host details: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemInfoViewSet(viewsets.ModelViewSet):
    serializer_class = SystemInfoSerializer

    def get_queryset(self):
        # Return only the latest system info per host
        time_threshold = timezone.now() - timedelta(seconds=10)
        return SystemInfo.objects.filter(updated_at__gte=time_threshold).order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        try:
            if isinstance(request.data, list):
                logger.info(f"Received {len(request.data)} system info records")
                serializer = self.get_serializer(data=request.data, many=True)
            else:
                logger.info("Received single system info record")
                serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            logger.info("System info saved successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error saving system info: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ New endpoint: /api/system-info/host/<hostname>/
    @action(detail=False, methods=["get"], url_path="host/(?P<hostname>[^/.]+)")
    def host_system_info(self, request, hostname=None):
        try:
            system_info = SystemInfo.objects.filter(hostname=hostname).order_by('-updated_at').first()
            if not system_info:
                return Response({"error": f"No system info found for host {hostname}"}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(system_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching system info for {hostname}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
