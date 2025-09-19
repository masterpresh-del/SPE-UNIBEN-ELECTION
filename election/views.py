
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Position, Candidate, Vote, VoterProfile
from django.contrib.auth.models import User
from django.db import IntegrityError

def index(request):
    return render(request, 'index.html')

def voter_login(request):
    if request.method=='POST':
        matric = request.POST.get('matric')
        password = request.POST.get('password')
        user = authenticate(request, username=matric, password=password)
        if user is not None:
            login(request, user)
            # ensure profile exists
            prof, _ = VoterProfile.objects.get_or_create(user=user)
            if prof.needs_reset:
                return redirect('reset_password')
            return redirect('vote')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def reset_password(request):
    prof, _ = VoterProfile.objects.get_or_create(user=request.user)
    if request.method=='POST':
        np = request.POST.get('new_password')
        if len(np) < 6:
            messages.error(request, 'Password too short')
        else:
            request.user.set_password(np)
            request.user.save()
            prof.needs_reset = False
            prof.save()
            messages.success(request, 'Password changed — please login again')
            return redirect('login')
    return render(request, 'reset.html')

@login_required
def vote_view(request):
    # show positions with candidates
    positions = Position.objects.prefetch_related('candidates').all()
    return render(request, 'vote.html', {'positions': positions})

@login_required
def cast_vote(request):
    if request.method!='POST':
        return redirect('vote')
    cid = request.POST.get('candidate_id')
    try:
        candidate = Candidate.objects.get(pk=cid)
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate not found'); return redirect('vote')
    # ensure voter hasn't voted for this position yet
    existing = Vote.objects.filter(voter=request.user, candidate__position=candidate.position)
    if existing.exists():
        messages.error(request, 'You have already voted for this position')
        return redirect('vote')
    try:
        Vote.objects.create(voter=request.user, candidate=candidate)
        # send confirmation email (simple)
        from django.core.mail import EmailMessage
        import qrcode, io, base64
        buf = io.BytesIO()
        qrcode.make(request.build_absolute_uri('/vote/')).save(buf, format='PNG')
        buf.seek(0)
        email = EmailMessage('Vote confirmation', f'Thank you {request.user.get_full_name() or request.user.username} — your vote for {candidate.name} was recorded.', to=[request.user.email])
        email.attach('qrcode.png', buf.read(), 'image/png')
        email.send(fail_silently=True)
        messages.success(request, 'Vote recorded — confirmation email sent')
    except IntegrityError:
        messages.error(request, 'Could not record vote')
    return redirect('vote')

@login_required
def results(request):
    # only staff/admin can view
    if not request.user.is_staff:
        messages.error(request, 'Not authorized')
        return redirect('index')
    # aggregate counts per candidate
    from django.db.models import Count
    data = Candidate.objects.annotate(votes=Count('vote')).order_by('-votes')
    return render(request, 'results.html', {'data': data})

@login_required
def subadmin_results(request):
    # only subadmins
    prof = getattr(request.user, 'profile', None)
    if not prof or not prof.is_subadmin:
        messages.error(request, 'Not authorized for subadmin')
        return redirect('index')
    from django.db.models import Count
    data = Candidate.objects.annotate(votes=Count('vote')).order_by('-votes')
    return render(request, 'subadmin_results.html', {'data': data})
