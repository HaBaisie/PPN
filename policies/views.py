from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from .models import Policy, Comment, Like, Reshare, ChatMessage
from .forms import PolicyForm, CommentForm
import csv
import json
from django.core.serializers import serialize


@login_required
def dashboard(request):
    policies = Policy.objects.all()
    for policy in policies:
        policy.ai_insights = policy.get_ai_insights()

    # EDA data for charts
    # Sentiment distribution across comments
    all_comments = Comment.objects.all()
    sentiment_counts = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
    for c in all_comments:
        # reuse policy sentiment logic loosely
        text = (c.text or '').lower()
        if any(w in text for w in ['good', 'positive', 'support', 'great', 'benefit']):
            sentiment_counts['Positive'] += 1
        elif any(w in text for w in ['bad', 'negative', 'oppose', 'poor', 'harm']):
            sentiment_counts['Negative'] += 1
        else:
            sentiment_counts['Neutral'] += 1

    # Top policies by popularity
    top_policies = []
    for p in policies:
        popularity = p.like_set.count() + p.reshare_set.count()
        top_policies.append({'name': p.name, 'popularity': popularity})
    top_policies = sorted(top_policies, key=lambda x: x['popularity'], reverse=True)[:5]

    # Comments over time (by day)
    comments = Comment.objects.order_by('created_at')
    comments_by_day = {}
    for c in comments:
        day = c.created_at.date().isoformat()
        comments_by_day[day] = comments_by_day.get(day, 0) + 1

    # Top commenters
    commenter_counts = {}
    for c in all_comments:
        name = c.user.username
        commenter_counts[name] = commenter_counts.get(name, 0) + 1
    top_commenters = sorted([{'user': k, 'count': v} for k, v in commenter_counts.items()], key=lambda x: x['count'], reverse=True)[:6]

    # Engagement by policy for pie chart
    engagement = []
    for p in policies:
        likes = p.like_set.count()
        reshares = p.reshare_set.count()
        engagement.append({'name': p.name, 'likes': likes, 'reshares': reshares, 'total': likes + reshares})
    engagement = sorted(engagement, key=lambda x: x['total'], reverse=True)[:6]

    # Recent chat messages
    recent_messages = ChatMessage.objects.order_by('-created_at')[:50]

    context = {
        'policies': policies,
        'sentiment_counts': json.dumps(sentiment_counts),
        'top_policies': json.dumps(top_policies),
        'comments_by_day': json.dumps(comments_by_day),
        'recent_messages': recent_messages[::-1],
        'top_commenters': json.dumps(top_commenters),
        'engagement': json.dumps(engagement),
    }
    # Totals
    context['total_likes'] = Like.objects.count()
    context['total_reshares'] = Reshare.objects.count()
    return render(request, 'dashboard.html', context)

def home(request):
    # Public homepage with awareness content
    sample_images = [
        'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80&auto=format&fit=crop'
    ]
    avatars = [f'https://i.pravatar.cc/150?img={i}' for i in range(1,7)]
    return render(request, 'home.html', {'images': sample_images, 'avatars': avatars})


def trendings(request):
    # List all reshares (most recent first)
    reshared = Reshare.objects.select_related('user', 'policy').order_by('-created_at')
    for r in reshared:
        r.share_url = request.build_absolute_uri(reverse('policy_detail', args=[r.policy.pk]))
    return render(request, 'trendings.html', {'reshared': reshared})


@login_required
def policy_detail(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    comments = Comment.objects.filter(policy=policy, parent=None)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.policy = policy
            comment.user = request.user
            if 'parent' in request.POST and request.POST.get('parent'):
                comment.parent_id = request.POST['parent']
            comment.save()
            return redirect('policy_detail', pk=pk)
    else:
        form = CommentForm()
    ai_insights = policy.get_ai_insights()
    # whether current user has liked or reshared this policy
    user_liked = Like.objects.filter(policy=policy, user=request.user).exists()
    user_reshared = Reshare.objects.filter(policy=policy, user=request.user).exists()
    return render(request, 'policy_detail.html', {'policy': policy, 'comments': comments, 'form': form, 'ai_insights': ai_insights, 'user_liked': user_liked, 'user_reshared': user_reshared})


@login_required
def like_policy(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    like_qs = Like.objects.filter(policy=policy, user=request.user)
    if like_qs.exists():
        # unlike
        like_qs.delete()
    else:
        Like.objects.create(policy=policy, user=request.user)
    return redirect('policy_detail', pk=pk)


@login_required
def reshare_policy(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    rs_qs = Reshare.objects.filter(policy=policy, user=request.user)
    if rs_qs.exists():
        # unshare
        rs_qs.delete()
    else:
        Reshare.objects.create(policy=policy, user=request.user)
    return redirect('policy_detail', pk=pk)


@login_required
def add_policy(request):
    if request.user.user_type != 'policymaker':
        return redirect('dashboard')
    if request.method == 'POST':
        form = PolicyForm(request.POST)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.added_by = request.user
            policy.save()
            return redirect('dashboard')
    else:
        form = PolicyForm()
    return render(request, 'add_policy.html', {'form': form})


@login_required
def analyst_extract(request, pk):
    if request.user.user_type != 'analyst':
        return redirect('dashboard')
    policy = get_object_or_404(Policy, pk=pk)
    comments = policy.comment_set.all()
    likes = policy.like_set.count()
    reshares = policy.reshare_set.count()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{policy.name}_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type', 'User', 'Text/Content', 'Date'])
    writer.writerow(['Likes', '', likes, ''])
    writer.writerow(['Reshares', '', reshares, ''])
    for comment in comments:
        writer.writerow(['Comment', comment.user.username, comment.text, comment.created_at])
    return response


@login_required
def chat_messages(request):
    msgs = ChatMessage.objects.order_by('-created_at')[:100]
    data = [{'user': m.user.username, 'user_id': m.user.id, 'message': m.message, 'created_at': m.created_at.isoformat()} for m in msgs[::-1]]
    return JsonResponse({'messages': data})


@login_required
@require_POST
def post_chat_message(request):
    text = request.POST.get('message')
    if not text:
        return JsonResponse({'error': 'No message provided'}, status=400)
    msg = ChatMessage.objects.create(user=request.user, message=text, created_at=timezone.now())
    return JsonResponse({'ok': True, 'user': msg.user.username, 'message': msg.message, 'created_at': msg.created_at.isoformat()})
