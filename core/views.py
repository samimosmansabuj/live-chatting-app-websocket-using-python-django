from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message, Attachment, CustomOffer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate



def homePage(request):
    return render(request, "home.html")

ALLOWED_MIME_PREFIXES = ("image/", "video/", "audio/", "pdf/")  # files allowed too, see below
MAX_FILE_MB = 25

@login_required
@require_POST
def upload_attachment(request, room_uuid):
    print("room_uuid: ", room_uuid)
    room = get_object_or_404(ChatRoom, uuid=room_uuid)
    if request.user not in (room.user1, room.user2):
        return HttpResponseForbidden("Not allowed")

    file = request.FILES.get("file")
    message = request.POST.get("message", "")
    print("file: ", file)
    if not file:
        return JsonResponse({"ok": False, "error": "No file"}, status=400)

    if file.size > MAX_FILE_MB * 1024 * 1024:
        return JsonResponse({"ok": False, "error": f"Max {MAX_FILE_MB}MB"}, status=400)

    mime = getattr(file, "content_type", "") or ""
    if mime.startswith("image/"):
        mtype = Message.IMAGE
    elif mime.startswith("video/"):
        mtype = Message.VIDEO
    elif mime.startswith("audio/"):
        mtype = Message.AUDIO
    else:
        mtype = Message.FILE
    
    msg = Message.objects.create(room=room, sender=request.user, type=mtype, content=message)

    att = Attachment.objects.create(
        message=msg,
        file=file,
        mime=mime,
        name=getattr(file, "name", ""),
        size=file.size,
    )

    return JsonResponse({
        "ok": True,
        "message_id": msg.id,
        "message": msg.content,
        "type": mtype,
        "attachment": {
            "url": att.file.url,
            "mime": att.mime,
            "name": att.name,
            "size": att.size,
        }
    }, status=201)

@login_required
@require_POST
def create_offer(request, room_uuid):
    room = get_object_or_404(ChatRoom, uuid=room_uuid)
    if request.user not in (room.user1, room.user2):
        return HttpResponseForbidden("Not allowed")

    import json
    payload = json.loads(request.body or "{}")

    msg = Message.objects.create(room=room, sender=request.user, type=Message.OFFER, content="")
    offer = CustomOffer.objects.create(
        message=msg,
        title=payload.get("title", ""),
        description=payload.get("description", ""),
        currency=(payload.get("currency") or "USD").upper(),
        amount_cents=int(payload.get("amount_cents") or 0),
        delivery_days=int(payload.get("delivery_days") or 1),
        status=CustomOffer.SENT
    )
    
    return JsonResponse({
        "ok": True,
        "message_id": msg.id,
        "message": msg.content,
        "type": Message.OFFER,
        "offer": {
            "id": offer.id,
            "title": offer.title,
            "description": offer.description,
            "currency": offer.currency,
            "amount_cents": offer.amount_cents,
            "delivery_days": offer.delivery_days,
            "status": offer.status,
        }
    }, status=201)

@login_required
@require_http_methods(["POST"])
def offer_action(request, room_uuid, message_id):
    room = get_object_or_404(ChatRoom, uuid=room_uuid)
    if request.user not in (room.user1, room.user2):
        return HttpResponseForbidden("Not allowed")

    msg = get_object_or_404(Message, id=message_id, room=room, type=Message.OFFER)
    offer = msg.offer
    import json
    action = (json.loads(request.body or "{}").get("action") or "").lower()
    if action == "accept":
        offer.status = CustomOffer.ACCEPTED
    elif action == "decline":
        offer.status = CustomOffer.DECLINED
    elif action == "cancel" and request.user == msg.sender:
        offer.status = CustomOffer.CANCELED
    else:
        return JsonResponse({"ok": False, "error": "Invalid action"}, status=400)
    offer.save()

    return JsonResponse({"ok": True, "status": offer.status})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender != request.user:
        return JsonResponse({'error': 'You can only delete your own messages'}, status=403)
    
    if hasattr(message, 'offer'):
        message.offer.delete()
    for file in message.attachments.all():
        file.delete()
    message.delete() 
    return JsonResponse({
        "ok": True,
        "message_id": message_id,
        "message": "Message Delete",
        "type": "delete",
    }, status=201)





@login_required(login_url="login")
def chat_room(request, room_uuid):
    room = get_object_or_404(ChatRoom, uuid=room_uuid)
    if request.user != room.user1 and request.user != room.user2:
        return HttpResponseForbidden("Not allowed")
    db_messages = Message.objects.filter(room=room)
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'db_messages': db_messages,
        'user_name': room.user1.username if room.user1 != request.user else room.user2.username
    })

@login_required(login_url="login")
def user_list(request):
    users = User.objects.all().exclude(id=request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})

@login_required(login_url="login")
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    user1, user2 = sorted([request.user, other_user], key=lambda u: u.id)

    room, created = ChatRoom.objects.get_or_create(user1=user1, user2=user2)
    return redirect('chat-room', room_uuid=room.uuid)

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("user-list")

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1 != password2:
            messages.warning(request, "Password doesn't match.")
            return redirect(request.META["HTTP_REFERER"])
        
        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username is already taken.")
            return redirect(request.META["HTTP_REFERER"])
        
        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email is already taken.")
            return redirect(request.META["HTTP_REFERER"])
        
        user = User.objects.create(username=username, email=email)
        user.set_password(password1)
        user.save()
        login(request, user)
        return redirect("user-list")
    return render(request, "registration.html")

