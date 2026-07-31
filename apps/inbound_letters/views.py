from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import InboundLetter, Sender
from .forms import InboundLetterForm, SenderForm

@login_required
def inbound_list(request):
    letters = InboundLetter.objects.all()
    return render(request, "inbound_letters/inbound_list.html", {"letters": letters})

@login_required
def inbound_detail(request, pk):
    letter = get_object_or_404(InboundLetter, pk=pk)
    return render(request, "inbound_letters/inbound_detail.html", {"letter": letter})

@login_required
def inbound_create(request):
    if request.method == "POST":
        form = InboundLetterForm(request.POST, request.FILES)
        if form.is_valid():
            letter = form.save(commit=False)
            import uuid
            letter.tracking_code = f"IN-{uuid.uuid4().hex[:8].upper()}"
            letter.registered_by = request.user
            letter.save()
            return redirect("inbound_detail", pk=letter.pk)
    else:
        form = InboundLetterForm()
    return render(request, "inbound_letters/inbound_form.html", {"form": form})

@login_required
def sender_list(request):
    senders = Sender.objects.all()
    return render(request, "inbound_letters/sender_list.html", {"senders": senders})

@login_required
def sender_create(request):
    if request.method == "POST":
        form = SenderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sender_list")
    else:
        form = SenderForm()
    return render(request, "inbound_letters/sender_form.html", {"form": form})
