from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from apps.operations.models import UserFavorite, CourseComments, Banner
from apps.operations.forms import UserFavForm, CommentsForm
from apps.courses.models import Course
from apps.organizations.models import CourseOrg, Teacher


class IndexView(View):
    """
    首页
    """
    def get(self, request, *args, **kwargs):
        # 制造403异常
        # from django.core.exceptions import PermissionDenied
        # raise PermissionDenied
        #
        banners = Banner.objects.all().order_by("index")
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, "index.html", {
            "banners": banners,
            "courses": courses,
            "banner_courses":banner_courses,
            "course_orgs":course_orgs
        })


class CommentView(View):
    def post(self, request, *args, **kwargs):
        """
        用户评论
        """
        # 如果用户未登录,就给前端返回对应的js数据
        # is_authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "fail",
                "msg": "用户未登录"
            })
        # 先表单验证
        comment_form = CommentsForm(request.POST)
        if comment_form.is_valid():
            course = comment_form.cleaned_data["course"]
            comments = comment_form.cleaned_data["comments"]

            comment = CourseComments()
            comment.user = request.user
            comment.comments = comments
            comment.course = course
            comment.save()

            return JsonResponse({
                "status": "success",
        })

        else:
            # 返回数据给前端
            return JsonResponse({
                "status": "fail",
                "msg": "参数错误"
            })


class AddFavView(View):
    def post(self, request, *args, **kwargs):
        """
        用户收藏，取消收藏
        """
        # 如果用户未登录,就给前端返回对应的js数据
        # is_authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "fail",
                "msg": "用户未登录"
            })
        # 先表单验证
        user_fav_form = UserFavForm(request.POST)
        if user_fav_form.is_valid():
            fav_id = user_fav_form.cleaned_data["fav_id"]
            fav_type = user_fav_form.cleaned_data["fav_type"]

            # 判断是否已经收藏,对数据库进行查询筛选
            existed_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
            if existed_records:
                # 已经收藏，本次操作是取消收藏
                existed_records.delete()

                """
                收藏人数变化
                """
                if fav_type == 1:
                    # 这是收藏课程,通过id找到
                    course = Course.objects.get(id=fav_id)
                    course.fav_nums -= 1  # 取消收藏，人数减一
                    course.save()

                elif fav_type == 2:
                    # 这是收藏课程机构,通过id找到
                    course_org = CourseOrg.objects.get(id=fav_id)
                    course_org.fav_nums -= 1  # 取消收藏，人数减一
                    course_org.save()

                elif fav_type == 3:
                    # 这是收藏讲师,通过id找到
                    teacher = Teacher.objects.get(id=fav_id)
                    teacher.fav_nums -= 1  # 取消收藏，人数减一
                    teacher.save()

                # 返回数据给前端
                return JsonResponse({
                    "status": "success",
                    "msg": "收藏"
                })

            # 用户收藏
            else:
                user_fav = UserFavorite()
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                user_fav.user = request.user
                user_fav.save()

                # 返回数据给前端
                return JsonResponse({
                    "status": "success",
                    "msg": "已收藏"
                })

        # 表单验证失败
        else:
            # 返回数据给前端
            return JsonResponse({
                "status": "fail",
                "msg": "参数错误"
            })

