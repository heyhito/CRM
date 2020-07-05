from django.db import models
# Create your models here.

# 职位表
class Role(models.Model):
    name = models.CharField(max_length=16)
    permissions = models.ManyToManyField(to='Permission')

    def __str__(self):
        return self.name


# 用户表
class User(models.Model):
    # name = models.CharField(max_length=16)
    # password = models.CharField(max_length=32)
    roles = models.ManyToManyField(Role)
    # user = models.OneToOneField('UserInfo')
    class Meta:
        abstract = True  # 执行数据库迁移指令时，不会将这个类生成表


# 菜单表
class Menu(models.Model):
    """

    一级菜单表
    """
    title = models.CharField(max_length=16)
    weight = models.IntegerField(default=0)
    icon = models.CharField(max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title', 'weight')


# 权限表
class Permission(models.Model):

    url = models.CharField(max_length=36)
    title = models.CharField(max_length=16)
    menu = models.ForeignKey(to='Menu', null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    url_name = models.CharField(max_length=32, default='1')

    def __str__(self):
        return self.title