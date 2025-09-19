
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Position, Candidate, Vote, VoterProfile
from django.contrib.auth.models import User
from django.db import IntegrityError

# FRONT PAGE — includes login form
def index(request):
    if request.method=='POST':
        matric = request.POST.get('matric')
        password = request.POST.get('password')
        user = authenticate(request, username=matric, password=password)
        if user is not None:
            login(request, user)
            prof, _ = VoterProfile.objects.get_or_create(user=user)
            if prof.needs_reset:
                return redirect('reset_password')
            return redirect('vote')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'index.html')  # index.html now has login panel

# LOGOUT
def user_logout(request):
    logout(request)
    return redirect('index')

# RESET PASSWORD
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
            return redirect('index')
    return render(request, 'reset.html')

# VOTING PAGE
@login_required
def vote_view(request):
    positions = Position.objects.prefetch_related('candidates').all()
    return render(request, 'vote.html', {'positions': positions})

# CAST VOTE
@login_required
def cast_vote(request):
    if request.method!='POST':
        return redirect('vote')
    cid = request.POST.get('candidate_id')
    try:
        candidate = Candidate.objects.get(pk=cid)
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate not found')
        return redirect('vote')
    existing = Vote.objects.filter(voter=request.user, candidate__position=candidate.position)
    if existing.exists():
        messages.error(request, 'You have already voted for this position')
        return redirect('vote')
    try:
        Vote.objects.create(voter=request.user, candidate=candidate)
        messages.success(request, f'Vote for {candidate.name} recorded')
    except IntegrityError:
        messages.error(request, 'Could not record vote')
    return redirect('vote')

# RESULTS — only staff
@login_required
def results(request):
    if not request.user.is_staff:
        messages.error(request, 'Not authorized')
        return redirect('index')
    from django.db.models import Count
    data = Candidate.objects.annotate(votes=Count('vote')).order_by('-votes')
    return render(request, 'results.html', {'data': data})

# SUBADMIN RESULTS
@login_required
def subadmin_results(request):
    prof = getattr(request.user, 'profile', None)
    if not prof or not prof.is_subadmin:
        messages.error(request, 'Not authorized for subadmin')
        return redirect('index')
    from django.db.models import Count
    data = Candidate.objects.annotate(votes=Count('vote')).order_by('-votes')
    return render(request, 'subadmin_results.html', {'data': data})
