import xadmin
from xadmin.layout import Fieldset, Main, Side, Row, FormHelper

from apps.courses.models import Course, Lesson, Video, CourseResource, CourseTag


class GlobalSettings(object):
    site_title = "鱼书后台管理系统"
    site_footer = "鱼书在线"
    # menu_style = "accordion"


class BaseSettings(object):
    enable_themes = True
    use_bootswatch = True


class CourseAdmin(object):
    # 添加默认显示列
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    # 添加可收索关键字
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    # 设置过滤字段
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    # 直接在列表页修改
    list_editable = ["degree", "desc"]


class NewCourseAdmin(object):
    # 添加默认显示列
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    # 添加可收索关键字
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    # 设置过滤字段
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    # 直接在列表页修改
    list_editable = ["degree", "desc"]

    style_fields = {
        "detail": "ueditor"
    }

    def get_form_layout(self):
        if self.org_obj:
            self.form_layout = (
                    Main(
                        Fieldset("讲师信息",
                                 'teacher', 'course_org',
                                 css_class='unsort no_title'
                                 ),
                        Fieldset("基本信息",
                                 'name', 'desc',
                                 Row('learn_times', 'degree'),
                                 Row('category', 'tag'),
                                 'youneed_know', 'teacher_tell', 'detail',
                                 ),
                    ),
                    Side(
                        Fieldset("访问信息",
                                 'fav_nums', 'click_nums', 'students', 'add_time'
                                 ),
                    ),
                    Side(
                        Fieldset("选择信息",
                                 'is_banner', 'is_classics'
                                 ),
                    )
            )
        return super(NewCourseAdmin, self).get_form_layout()


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'file', 'add_time']
    search_fields = ['course', 'name', 'file']
    list_filter = ['course', 'name', 'file', 'add_time']


class CourseTagAdmin(object):
    list_display = ['course', 'tag', 'add_time']
    search_fields = ['course', 'tag']
    list_filter = ['course', 'tag', 'add_time']


# xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Course, NewCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(CourseTag, CourseTagAdmin)
xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings)
xadmin.site.register(xadmin.views.BaseAdminView, BaseSettings)
