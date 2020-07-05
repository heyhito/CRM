
from collections import OrderedDict

from django.conf import settings
from django import template

register = template.Library()


@register.inclusion_tag('rbac/menu.html')
def menu(request):
    menu_dict = request.session.get(settings.MENU_KEY)
    # 菜单栏排序
    order_dict = OrderedDict()
    keys = sorted(menu_dict, key=lambda x: menu_dict[x]['weight'], reverse=True)
    for key in keys:
        order_dict[key] = menu_dict[key]
    # 一级菜单展开状态保留
    for key, value in order_dict.items():
        # value['class'] = 'hidden'
        for i in value['children']:
            # i.get('id')：二级菜单的id
            if request.current_id == i.get('id'):
                value['class'] = 'show'
                i['class'] = 'active'

    # 给菜单添加点击选中效果
    # for i in menu_dict:
    #     if re.match(i['permissions__url'], path):
    #         i['class'] = 'active'
    return {'order_dict': order_dict}

# 精确到按钮级别的URL过滤器
@register.filter
def url_filter(request, url_name):
    if url_name in request.session.get('url_name'):
        return True
    else:
        return False

# 面包屑
@register.inclusion_tag('rbac/bread_crumbs.html')
def breadcrumb(request):
    bread_crumb = request.bread_crumb
    return {'bread_crumb': bread_crumb}


@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params._mutable = True
    params['rid'] = rid
    # params: < QueryDict: {'uid': ['2'], 'rid': [1]} >
    return params.urlencode()