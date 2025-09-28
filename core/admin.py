from django.contrib import admin
from .models import *

admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Attachment)
admin.site.register(CustomOffer)