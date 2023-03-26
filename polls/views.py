from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice


# Create your views here.
def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # output = ', '.join([q.question_text for q in latest_question_list])
    # return HttpResponse(output)
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    # return HttpResponse("You're looking at question %s." % question_id)
    # try:
    #     question = Question.objects.get(pk=question_id)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")
    # return render(request, 'polls/detail.html', {'question': question})
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    # response = "You're looking at the results of question %s."
    # return HttpResponse(response % question_id)
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


# 改良视图
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    # def get_queryset(self):
    #     """Return the last five published questions."""
    #     return Question.objects.order_by('-pub_date')[:5]
    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        返回一个包含pub_date小于或等于-即早于或等于- timezone.now的问题的查询集。
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    # return HttpResponse("You're voting on question %s." % question_id)
    question = get_object_or_404(Question, pk=question_id)
    try:
        # request.POST 是一个类字典对象，让你可以通过关键字的名字获取提交的数据。
        # 这个例子中 request.POST['choice'] 以字符串形式返回选择的 Choice 的 ID。
        # request.POST 的值永远是字符串。
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        # 如果在 request.POST['choice'] 数据中没有提供 choice，POST 将引发一个 KeyError。
        # 上面的代码检查 KeyError，如果没有给出 choice 将重新显示 Question 表单和一个错误信息。
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        # 正如上面的Python注释指出的，在成功处理POST数据后，你应该总是返回一个
        # HttpResponseRedirect。这不是Django的特殊要求，这是那些优秀网站在开发实践中形成的共识。
        # 在这个例子中，我们在HttpResponseRedirect的构造函数中使用reverse()函数。
        # 这个函数避免了我们在视图函数中硬编码URL。
        # 它需要我们给出我们想要跳转的视图的名字和该视图所对应的URL
        # 模式中需要给该视图提供的参数。
        # 在本例中，使用在教程第3部分中设定的URLconf，
        # reverse()调用将返回一个这样的字符 '/polls/3/results/'
        # 其中 3 是 question.id 的值。重定向的 URL 将调用 'results' 视图来显示最终的页面。
