from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from apps.courses.models import Course, CourseTag, CourseResource, Video
from apps.operations.models import UserFavorite, UserCourse, CourseComments


class VideoView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, course_id, video_id, *args, **kwargs):
        """
        获取课程视频
        """
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        video = Video.objects.get(id=int(video_id))

        # 1.用户和课程之间的关联
        # 查询用户是否已经关联该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            course.students += 1
            course.save()

        # 学习过该课程的同学
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]  # 拿到了学过该课程的所有学生id
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]  # 取出所有id对应同学的所有课程
        # related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:
                related_courses.append(item.course)

        # 该课程资源
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, "course-play.html", {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
            "video": video
        })


class CourseCommentView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, course_id,  *args, **kwargs):
        """
        课程评论
        """
        course = Course.objects.get(id=int(course_id))
        # 点击一次，点击数加1
        course.click_nums += 1
        course.save()

        # 获取课程评论
        comments = CourseComments.objects.filter(course=course)

        # 1.用户和课程之间的关联
        # 查询用户是否已经关联该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            course.students += 1
            course.save()

        # 学习过该课程的同学
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]  # 拿到了学过该课程的所有学生id
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[
                      :5]  # 取出所有id对应同学的所有课程
        # related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:
                related_courses.append(item.course)

        # 该课程资源
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, "course-comment.html", {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
            "comments": comments
        })


class CourseLessonView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, course_id,  *args, **kwargs):
        """
        获取课程章节信息
        """
        course = Course.objects.get(id=int(course_id))
        # 点击一次，点击数加1
        course.click_nums += 1
        course.save()

        # 1.用户和课程之间的关联
        # 查询用户是否已经关联该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            course.students += 1
            course.save()

        # 学习过该课程的同学
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]  # 拿到了学过该课程的所有学生id
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]  # 取出所有id对应同学的所有课程
        # related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:
                related_courses.append(item.course)

        # 该课程资源
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, "course-video.html", {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses
        })


class CourseDetailView(View):
    def get(self, request, course_id,  *args, **kwargs):
        """
        获取课程详情
        """
        course = Course.objects.get(id = int(course_id))
        # 点击一次，点击数加1
        course.click_nums += 1
        course.save()

        # 获取收藏状态
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 通过课程标签找到相关课程推荐
        # tag = course.tag
        # related_courses = []
        # if tag:
        #     related_courses = Course.objects.filter(tag=tag).exclude(id=course.id)[:3]
        tags = course.coursetag_set.all()
        tag_list = [tag.tag for tag in tags]
        # for tag in tags:
        #     tag_list.append(tag.tag)

        course_tags = CourseTag.objects.filter(tag__in=tag_list).exclude(course__id=course.id)
        related_courses = set()
        for course_tag in course_tags:
            related_courses.add(course_tag.course)

        return render(request, "course-detail.html", {
            "course": course,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
            "related_courses": related_courses
        })


class CourseListView(View):
    def get(self, request, *args, **kwargs):
        """
        获取课程列表信息
        """
        all_courses = Course.objects.order_by("-add_time")
        # 右侧热门推荐
        hot_courses = Course.objects.order_by("-click_nums")[:3]

        # 搜索关键词
        keywords = request.GET.get("keywords", "")
        s_type = "course"
        if keywords:
            # or 搜索
            all_courses = all_courses.filter(Q(name__icontains=keywords)|Q(desc__icontains=keywords)|Q(detail__icontains=keywords))


        # 课程排序
        sort = request.GET.get("sort", "")
        # 根据参与人数排序
        if sort == "students":
            all_courses = all_courses.order_by("-students")
        # 根据最热门排序
        elif sort == "hot":
            all_courses = all_courses.order_by("-click_nums")

        # 对课程机构数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 对课程机构数据进行分页
        p = Paginator(all_courses, per_page=6, request=request)
        courses = p.page(page)

        return render(request, "course-list.html", {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses,
            "keywords": keywords,
            "s_type": s_type
        })
