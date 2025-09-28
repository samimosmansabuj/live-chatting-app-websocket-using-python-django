from django.db import models
from django.contrib.auth.models import User
import uuid

class ChatRoom(models.Model):
    uuid = models.CharField(max_length=255, blank=True, null=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatroom1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatroom2")
    created_at = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4().hex
        return super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('user1', 'user2')
    
    def __str__(self):
        return f"ChatRoom: {self.user1.email} & {self.user2.email}"

class Message(models.Model):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE  = "file"
    OFFER = "offer"
    TYPE_CHOICES = [(TEXT, "Text"), (IMAGE, "Image"), (VIDEO, "Video"),(AUDIO, "Audio"), (FILE, "File"), (OFFER, "Offer")]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TEXT)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["timestamp"]
    
    def __str__(self):
        return f"{self.sender.email}: {self.content[:20]}"

class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="chat/")
    mime = models.CharField(max_length=100, blank=True, default="")
    name = models.CharField(max_length=255, blank=True, default="")
    size = models.BigIntegerField(default=0)

class CustomOffer(models.Model):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELED = "canceled"

    STATUS_CHOICES = [(DRAFT, "Draft"), (SENT, "Sent"), (ACCEPTED, "Accepted"), (DECLINED, "Declined"), (CANCELED, "Canceled")]
    
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=8, default="USD")
    amount_cents = models.PositiveIntegerField()  # store minor units
    delivery_days = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=SENT)


