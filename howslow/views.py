from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext
from django.conf import settings
import django
import timeit
import platform
import cProfile
import cStringIO
import pstats


def time_render(template_name, dict, req_context, times):
    return timeit.timeit(lambda: loader.render_to_string(template_name, dict, req_context),
                         number=times)


def make_django_tutorial_context():
    return {
        "error_message": "error!",
        "poll": {"question": "test_question",
                 "choice_set": {"all": [
                     {"id":x, "choice_text":"choice %s" % x}
                     for x in xrange(4)]
                 }}
    }


def make_results_context():
    return {"results": {"test": {"time_taken": 1, "per_call": 1},
                        "test2": {"time_taken": 1, "per_call": 1},
                        "test3": {"time_taken": 1, "per_call": 1}},
            "platform": {"django_version": 1,
                         "python_version": 2}}


def index(request):
    times = int(request.GET.get('times', 100))

    returner = {}

    for template_name in ["empty_template.html", "stackoverflow_homepage.html",
                          ("django_tutorial_page.html", make_django_tutorial_context),
                          ("results.html", make_results_context)]:
        ctx_dict = {}
        request_context = RequestContext(request)
        if isinstance(template_name, tuple):
            template_name, callable_or_ctx = template_name
            if isinstance(callable_or_ctx, dict):
                ctx_dict = callable_or_ctx
            else:
                ctx_dict = callable_or_ctx()

        time_taken = round(time_render(template_name, ctx_dict, request_context, times), 5)

        profile = cProfile.Profile()
        prof = profile.runctx("loader.render_to_string(template_name, ctx_dict, request_context)", globals(), locals())
        output = cStringIO.StringIO()
        pstats.Stats(prof, stream=output).strip_dirs().sort_stats(0).print_stats()

        returner[template_name] = {"time_taken": time_taken, "per_call": time_taken / times,
                                   "profile":output.getvalue()}

    return render_to_response("results.html", dictionary={"results":returner,
                                                          "platform":{
                                                              "django_version":django.get_version(),
                                                              "python_version":platform.python_version(),
                                                              "platform":platform.platform(),
                                                              "debug":settings.DEBUG
                                                          }})