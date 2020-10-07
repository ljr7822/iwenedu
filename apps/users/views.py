from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from pure_pagination import Paginator, PageNotAnInteger
import redis

from apps.users.forms import LoginForm, DynamicLoginForm, RegisterGetForm, UploadImageForm
from apps.users.forms import UserInfoForm, ChangePwdForm
from apps.utils.YunPian import send_single_sms
from apps.utils.random_str import generate_random
from django.contrib.auth.mixins import LoginRequiredMixin
from iwenedu.settings import yp_apikey, REDIS_HOST, REDIS_PORT
from apps.operations.models import UserCourse, UserFavorite, UserMessage, Banner
from apps.organizations.models import CourseOrg, Teacher
from apps.courses.models import Course


def message_nums(request):
    """
    Add media-related context variables to the context.
    """
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(has_read=False).count()}
    else:
        return {}


class MyMessageView(LoginRequiredMixin, View):
    """
    我的消息
    """
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "message"
        messages = UserMessage.objects.filter(user=request.user)

        for message in messages:
            message.has_read = True
            message.save()

        # 对消息数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(messages, per_page=1, request=request)
        messages = p.page(page)

        return render(request, "usercenter-message.html", {
            "messages": messages,
            "current_page": current_page
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    我的收藏——公开课
    """
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_course"
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            try:
                course = Course.objects.get(id=fav_course.fav_id)
                course_list.append(course)
            except Course.DoesNotExist as e:
                pass
        return render(request, "usercenter-fav-course.html", {
            "course_list": course_list,
            "current_page": current_page
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我的收藏——讲师
    """
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_teacher"
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            org = Teacher.objects.get(id=fav_teacher.fav_id)
            teacher_list.append(org)
        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list,
            "current_page": current_page
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    我的收藏——机构
    """
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfavorg"
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html",{
            "org_list": org_list,
            "current_page": current_page
        })


class MyCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "mycourse"
        my_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "my_courses": my_courses,
            "current_page": current_page
        })


class ChangePwdView(LoginRequiredMixin, View):
    """
    修改密码
    """
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            # pwd1 = request.POST.get("password1", "")
            # pwd2 = request.POST.get("password2", "")
            #
            # if pwd1 != pwd2:
            #     return JsonResponse({
            #         "status":"fail",
            #         "msg":"密码不一致"
            #     })
            pwd1 = request.POST.get("password1", "")
            user = request.user
            user.set_password(pwd1)
            user.save()
            # login(request, user)

            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(pwd_form.errors)


class UploadImageView(LoginRequiredMixin, View):
    """
    修改头像
    """
    login_url = "/login/"

    # def save_file(self, file):
    #     with open("E:/PycharmProjects/iwenedu/media/head_image/image.png")

    def post(self, request, *args, **kwargs):
        # 处理用户上传的头像
        # files = request.FILES["image"]
        # pass
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse({
                "status": "fail"
            })


class UserInfoView(LoginRequiredMixin, View):
    """
    修改个人数据
    """
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "info"
        captcha_form = RegisterGetForm()
        return render(request, "usercenter-info.html",{
            "captcha_form": captcha_form,
            "current_page": current_page
        })

    def post(self, request, *args, **kwargs):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(user_info_form.errors)


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()

        return render(request, "register.html", {"register_get_form": register_get_form})

    def post(self, request, *args, **kwargs):
        return render(request, "register.html")


class SendSmsView(View):
    """
    发送短信验证码
    """
    def post(self, request, *args, **kwargs):
        # 验证图片验证码
        send_sms_form = DynamicLoginForm(request.POST)
        # 保存前端是哪一个信息出错
        re_dict={}
        if send_sms_form.is_valid():
            # 获取手机号码
            mobile = send_sms_form.cleaned_data["mobile"]
            # 随机生成数字验证码
            code = generate_random(4, 0)
            # 发送验证码
            re_json = send_single_sms(yp_apikey, code, mobile=mobile)
            # 判断是否发送成功
            if re_json["code"] == 0:
                # 发送成功
                re_dict["status"] == "success"
                # redis 数据库操作
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
                r.set(str(mobile), code)
                r.exists(str(mobile), 60*5)
            else:
                # 发送失败
                re_dict["msg"] = re_json["msg"]
        else:
            # 查看前端出错信息并保存到 re_dict={}
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        return JsonResponse(re_dict)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    # 处理get请求
    def get(self, request, *args, **kwargs):
        # 判断用户是否登录
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))

        banners = Banner.objects.all()[:3]

        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        return render(request, "login.html", {
            "login_form": login_form,
            "next": next,
            "banners": banners
        })

    def post(self, request, *args, **kwargs):
        # 表单验证
        login_form = LoginForm(request.POST)

        banners = Banner.objects.all()[:3]

        if login_form.is_valid():
            # 获取表单的数据
            user_name = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            # 用于通过用户名和密码查询用户是否存在
            user = authenticate(username=user_name, password=password)
            if user is not None:
                # 查询到用户，登录
                login(request, user)
                # 登录成功之后应该怎么返回页面
                next = request.GET.get("next", "")
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect(reverse("index"))
            else:
                # 没有查询到用户

                return render(request, "login.html", {
                    "msg": "用户名或密码错误",
                    "login_form": login_form,
                    "banners": banners
                })
        else:
            return render(request, "login.html", {
                "login_form": login_form,
                "banners": banners
            })
