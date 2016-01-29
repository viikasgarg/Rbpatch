from django.views.generic import ListView, DetailView
from django.views.generic import CreateView
from django.core.urlresolvers import reverse_lazy
from patch.models import Patch
from django.template import RequestContext
from django.shortcuts import render_to_response
from rbtools.api.client import RBClient
from subprocess import check_output, STDOUT
import rbpatch.settings as settings
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

client = RBClient(settings.REVIEW_PATH)
root = client.get_root()


def run_command(command):
    output = ""
    try:
        output = check_output(command, stderr=STDOUT, cwd=settings.CODE_PATH)
    except:
        pass ## Just Ignoring error while runing the command  as return false
        ## occurs when try to revert non existing commit
    return output


def restart_server():
    return run_command(["ls"])
    return run_command(["sudo", "service", "uwsgi", "restart"])


def apply_patch(review_id):
    command = ["rbt", "patch", "-C", review_id]
    return run_command(command)


def check_if_already_applied(review_id):
    review_pattern = "/r/" + review_id + "/"
    command = ["git", "log", "--all", "--grep", review_pattern]
    return run_command(command)


def get_git_logs(count=settings.GIT_LOG_COUNT):
    count = "-" + str(count)
    command = ["git", "log", count]
    return run_command(command)

def revert_commit(commit_id):
    command = ["git", "revert", "--no-edit", commit_id]
    return run_command(command)

# Create your views here.


@login_required
def home(request):
    errors = ""
    success = ""
    commit_id = ""
    exist_errors = ""
    rbid = ""
    found = False
    if request.POST:
        p = Patch()
        p.submitter = request.user
        p.time = datetime.now()
        p.status = "failed"

        try:
            rbid = request.POST.get('rbid')
            p.pid = rbid
            root.get_review_request(review_request_id=rbid)
        except:
            errors = "Invalid Review ID : {}".format(rbid)
            p.info = errors
            p.save()
            return render_to_response('homepage.html', {
                'request': request,
                'success': success,
                'errors': errors,
            }, RequestContext(request, {}),)

        commit_id = request.POST.get('commit_id')
        if commit_id:
            reverted = revert_commit(commit_id)
            commit_id = ''
        else:
            found = check_if_already_applied(rbid)

        if not found:
            success = apply_patch(rbid)
            if success:
                success = "Successfully Applied patch id {} and restarted the server".format(
                    rbid)
                p.status = "success"
                p.info = success
                restart_server()
            else:
                errors += "Please resolve conflict on QA server. Contact Server Admins"
                p.info = errors
                p.status = "failed"
        else:
            commit_id = found.split()[1] if len(found.split()) > 1 else None
            exist_errors += "Already Found in repo: {}\n".format(rbid)
            exist_errors += found
            p.info = exist_errors
            p.status = "failed"

        p.save()

    return render_to_response('homepage.html', {
        'request': request,
        'success': success,
        'errors': errors,
        "exist_errors": exist_errors,
        'rbid':rbid,
        'commit_id':commit_id
    }, RequestContext(request, {}),)

# Create your views here.


@login_required
def gitlogs(request):
    return render_to_response('gitlog.html', {
        'request': request,
        "gitlogs": get_git_logs(),
    }, RequestContext(request, {}),)


class PatchList(ListView):
    model = Patch      # shorthand for setting queryset = models.Car.objects.all()
    # optional (the default is app_name/modelNameInLowerCase_list.html; which
    # will look into your templates folder for that path and file)
    template_name = 'patch/patch_list.html'
    # default is object_list as well as model's_verbose_name_list and/or
    # model's_verbose_name_plural_list, if defined in the model's inner Meta
    # class
    context_object_name = "patch_list"
    paginate_by = 10  # and that's it !!

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PatchList, self).dispatch(*args, **kwargs)


class PatchDetail(DetailView):
    model = Patch
    context_object_name = 'patch'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PatchDetail, self).dispatch(*args, **kwargs)
