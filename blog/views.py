from django.shortcuts import render
from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import LanguageTranslatorV3
from ibm_watson import ToneAnalyzerV3
from django.contrib.auth.decorators import login_required

authenticator = IAMAuthenticator('H_x_yOsbZ0CstPQQWO1NWpDB8NvOXOUfKZ5fEqR5Ngh2')
language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            authenticator=authenticator)

authenticatorTone = IAMAuthenticator('TzO1sOEHidzRCb8VqGO-Ki0St9Ac_7B-hcX9YB1vI-7T')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticatorTone
)

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    for post in posts:
        posting = post.text
        language_translator.set_service_url('https://gateway.watsonplatform.net/language-translator/api')
        language_translator.set_disable_ssl_verification(True)
        translation = language_translator.translate(
            text=post.text, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']

        tone_analyzer.set_service_url('https://gateway.watsonplatform.net/tone-analyzer/api')
        tone_analysis = tone_analyzer.tone(
            {'text': post.text}, content_type='application/json').get_result()
        tone = (json.dumps(tone_analysis, indent=2))
        tone2 = json.loads(tone)
        tone3 = str(tone)
        post.tone3 = tone3
        post.tonescore1 = ''
        post.tonename1 = ''
        post.tonename2 = ''
        post.tonescore2 = ''
        if len(tone2['document_tone']['tones']) > 0:
            post.tonescore1 = tone2['document_tone']['tones'][0]['score']
            post.tonename1 = tone2['document_tone']['tones'][0]['tone_name']
            if len(tone2['document_tone']['tones']) > 1:
                post.tonescore2 = tone2['document_tone']['tones'][1]['score']
                post.tonename2 = tone2['document_tone']['tones'][1]['tone_name']


    return render(request, 'blog/post_list.html', {'posts' : posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

