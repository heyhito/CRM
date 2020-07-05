import os
import random

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CRM.settings")
    import django
    django.setup()
    from sales import models

    source_type = (('qq', "qq群"),
                   ('referral', "内部转介绍"),
                   ('website', "官方网站"),
                   ('baidu_ads', "百度推广"),
                   ('office_direct', "直接上门"),
                   ('WoM', "口碑"),
                   ('public_class', "公开课"),
                   ('website_luffy', "路飞官网"),
                   ('others', "其它"),)

    course_choices = (('LinuxL', 'Linux中高级'),
                      ('PythonFullStack', 'Python高级全栈开发'),)

    sex_type = (('male', '男'), ('female', '女'))
    obj_list = []
    for i in range(251):
        dic = {
            'qq':random.randint(1000000000,9999999999),
            'name':'钢铁侠%s'%i,
            'source':source_type[random.randint(0,8)][0],
            'course':course_choices[random.randint(0,1)][0],
            'sex':sex_type[random.randint(0,1)][0],
        }
        obj = models.Customer(**dic)
        obj_list.append(obj)
    models.Customer.objects.bulk_create(obj_list)