import re

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import (reverse, redirect, HttpResponse)


class PermissionAuth(MiddlewareMixin):

    def process_request(self, request):
        # 登陆认证白名单
        white_list = [reverse('login'), '/admin/*', ]
        path = request.path
        request.current_id = None
        request.bread_crumb = []
        for i in white_list:
            if re.match(i, path):
                return
        # 登陆认证
        is_login = request.session.get('is_login')
        if not is_login:
            return redirect('login')

        # 权限认证白名单
        permission_white_list = ['/admin/*', ]
        if path in permission_white_list:
            return
        permission_dict = request.session.get('permission_dict')
        """
        [{
            'permissions__id': 1,
            'permissions__url': '/customer/list/',
            'permissions__title': '客户展示',
            'permissions__parent_id': None,
            'permissions__menu__id': 1,
            'permissions__menu__weight': 99,
            'permissions__menu__title': '客户管理',
            'permissions__menu__icon': 'fa-user-circle-o'
        }, {
            'permissions__id': 2,
            'permissions__url': '/customer/add/',
            'permissions__title': '添加客户',
            'permissions__parent_id': 1,
            'permissions__menu__id': None,
            'permissions__menu__weight': None,
            'permissions__menu__title': None,
            'permissions__menu__icon': None
        },
        """
        print(path, permission_dict['33']['permissions__url'])
        for permission in permission_dict.values():
            reg = r'^%s$' % (permission['permissions__url'])

            if re.match(reg, path):
                # 当前子权限的父级菜单权限的id，即添加客户权限从属于二级菜单客户管理的子权限
                pid = permission.get('permissions__parent_id')
                if pid:
                    # 如果拿到了pid，则当前访问的路径权限为该id的子权限
                    request.current_id = pid
                    request.bread_crumb.append(
                        {
                            'url': permission_dict[str(pid)]['permissions__url'],
                            'title': permission_dict[str(pid)]['permissions__title'],
                        }
                    )
                    request.bread_crumb.append(
                        {
                            'url': None,
                            'title': permission['permissions__title']
                        }
                    )
                else:
                    request.bread_crumb.append(
                        {
                            'url': None,
                            'title': permission['permissions__title']
                        }
                    )
                    request.current_id = permission.get('permissions__id')
                return
        else:
            return HttpResponse('您不配')
