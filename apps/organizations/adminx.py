import xadmin

from apps.organizations.models import Teacher, CourseOrg, City


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company']
    search_fields = ['org', 'name', 'work_years', 'work_company']
    list_filter = ['org', 'name', 'work_years', 'work_company']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums']
    style_fields = {"desc": "ueditor"}


class CityAdmin(object):
    # 添加默认显示列
    list_display = ["id", "name", "desc"]
    # 添加可收索关键字
    search_fields = ["name", "desc"]
    # 设置过滤字段
    list_filter = ["name", "desc", "add_time"]
    # 直接在列表页修改
    list_editable = ["name", "desc"]


xadmin.site.register(Teacher, TeacherAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(City, CityAdmin)
