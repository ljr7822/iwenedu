from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# 自定义 userprofile 表覆盖默认的 user 表
# 继承了 AbstractUser，添加我们需要的字段，手机号，头像，一对一关系

GENDER_CHOICES = (
    ("male", "男"),
    ("female", "女")
)


class BaseModel(models.Model):
    add_time = models.DateField(default=datetime.now, verbose_name="添加时间")

    # 避免生成一张表
    class Meta:
        abstract = True


class UserProfile(AbstractUser):
    # 昵称 最长为50 可空
    nick_name = models.CharField(max_length=50, verbose_name="昵称", default="")
    # 生日 允许为空
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    # 性别 必填
    gender = models.CharField(verbose_name="性别", choices=GENDER_CHOICES, max_length=6)
    # 地址 必填，如果一开始没有填，就设置为空 default=""
    address = models.CharField(max_length=100, verbose_name="地址", default="")
    # 手机号 不可为空,不能相同 unique=True
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    # 头像
    image = models.ImageField(verbose_name="用户头像", upload_to="head_image/%Y%m", default="default.jpg")

    class Meta:
        # verbose_name 给模型起一个更可读性的名字
        verbose_name = "用户信息"
        # verbose_name_plural 模型的复数形式指定
        verbose_name_plural = verbose_name

    def unread_nums(self):
        # 未读消息数量
        return self.usermessage_set.filter(has_read=False).count()

    # 定义__str__方法，直接输出对象名时，打印的是username的值
    def __str__(self):
        if self.nick_name:
            return self.nick_name
        else:
            return self.username
