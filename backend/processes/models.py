from django.db import models
from django.utils import timezone


class Process(models.Model):
    hostname = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    pid = models.IntegerField()
    name = models.CharField(max_length=255)
    parent_pid = models.IntegerField()
    cpu_percent = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField(default=0.0)
    net_usage = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=['hostname', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.hostname} - {self.name} ({self.pid})"


class SystemInfo(models.Model):
    # Basic host info
    name = models.CharField(max_length=255, default="Unknown")
    hostname = models.CharField(max_length=255, default="Unknown")
    operating_system = models.CharField(max_length=255, default="Unknown")
    processor = models.CharField(max_length=255, default="Unknown")

    # Hardware specs
    number_of_cores = models.IntegerField(default=0)
    number_of_threads = models.IntegerField(default=0)
    ram_gb = models.FloatField(default=0.0)
    used_ram_gb = models.FloatField(default=0.0)
    available_ram_gb = models.FloatField(default=0.0)

    # Storage
    storage_total_gb = models.FloatField(default=0.0)
    storage_used_gb = models.FloatField(default=0.0)
    storage_free_gb = models.FloatField(default=0.0)

    # Timestamp
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['hostname', 'updated_at']),
        ]

    def __str__(self):
        return f"{self.hostname} ({self.operating_system}) @ {self.updated_at}"
