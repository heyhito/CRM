from django.conf import settings


def add_permission(request, user_obj):
    request.session['is_login'] = True  # 记录用户是否登陆了
    permission_list = user_obj.roles.values(
        # 二级菜单数据
        'permissions__id',
        'permissions__url',
        'permissions__title',
        'permissions__url_name',
        'permissions__parent_id',
        # 一级菜单数据
        'permissions__menu__id',
        'permissions__menu__weight',
        'permissions__menu__title',
        'permissions__menu__icon',
    ).distinct()
    menu_dict = {}
    url_name_list = []
    for i in permission_list:
        url_name_list.append(i.get('permissions__url_name'))
        if i['permissions__menu__id']:
            if i['permissions__menu__id'] in menu_dict:
                menu_dict[i['permissions__menu__id']]['children'].append(
                    {
                        'url': i['permissions__url'],
                        'title': i['permissions__title'],
                        'id': i['permissions__id'],
                    }
                )
            else:
                menu_dict[i['permissions__menu__id']] = {
                    'title': i['permissions__menu__title'],
                    'icon': i['permissions__menu__icon'],
                    'weight': i['permissions__menu__weight'],
                    'children': [
                        {
                            'url': i['permissions__url'],
                            'title': i['permissions__title'],
                            'id': i['permissions__id'],
                        }
                    ]
                }
    permission_dict = {}
    for permission in permission_list:
        permission_dict[permission.get('permissions__id')] = permission
    # 权限注入
    request.session[settings.PERMISSION_KEY] = permission_dict
    # 菜单展示URL注入
    request.session[settings.MENU_KEY] = menu_dict
    # URL别名注入
    request.session['url_name'] = url_name_list
