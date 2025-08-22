from rest_framework import serializers
from .models import Process, SystemInfo


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = [
            'hostname',
            'timestamp',
            'pid',
            'name',
            'parent_pid',
            'cpu_percent',
            'memory_usage',
            'disk_usage',
            'net_usage'
        ]


class SystemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemInfo
        fields = [
            'hostname',
            'name',
            'operating_system',
            'processor',
            'num_cores',
            'num_threads',
            'ram_gb',
            'used_ram_gb',
            'available_ram_gb',
            'storage_free_gb',
            'storage_total_gb',
            'storage_used_gb',
            'updated_at'
        ]
