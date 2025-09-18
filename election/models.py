
from django.db import models
from django.contrib.auth.models import User

class Position(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Candidate(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    manifesto = models.TextField(blank=True)
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    def __str__(self): return f"{self.name} ({self.position.name})"

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('voter', 'candidate')  # ensure one vote per candidate; we'll enforce per position in logic
    def __str__(self): return f"{self.voter.username} -> {self.candidate.name}"

class VoterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    needs_reset = models.BooleanField(default=True)
    is_subadmin = models.BooleanField(default=False)
    def __str__(self): return f"Profile: {self.user.username}"
