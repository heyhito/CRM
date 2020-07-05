from django.shortcuts import (render, redirect, HttpResponse)
from django.utils.safestring import mark_safe
from django.db.models import Q
from django import forms
from django.forms import (modelformset_factory, formset_factory)

from rbac import models
from sales.models import UserInfo
from rbac.server.routes import all_url
from rbac.icon_data import icon_list
from rbac.forms import MultiPermissionForm

# Create your views here.


def role_list(request, ):
    all_roles = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'all_roles': all_roles})


class RoleForm(forms.ModelForm):
    class Meta:
        model = models.Role
        fields = '__all__'
        exclude = ['permissions', ]
        widgets = {
            'name': forms.widgets.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'name': '姓名'
        }


def role_add_edit(request, rid=None):
    role_obj = models.Role.objects.filter(id=rid).first()
    if request.method == 'GET':
        form_obj = RoleForm(instance=role_obj)
        return render(request, 'rbac/form.html', {'form_obj': form_obj})
    else:
        form_obj = RoleForm(request.POST, instance=role_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('rbac:role_list')
        else:
            return render(request, 'rbac/form.html', {'form_obj': form_obj})


def role_del(request, cid):
    models.Role.objects.filter(id=cid).delete()
    return redirect('rbac:role_list')


# 菜单展示
def menu_list(request):
    mid = request.GET.get('mid')
    all_menus = models.Menu.objects.all()
    if mid:
        all_permissions = models.Permission.objects.filter(
            Q(menu_id=mid) | Q(parent__menu_id=mid)).values('id', 'url', 'title',
                                                            'menu__title', 'menu_id', 'parent__title',
                                                            'url_name', 'parent_id')
    else:
        all_permissions = models.Permission.objects.all().values('id', 'url', 'title',
                                                                 'menu__title', 'menu_id', 'parent__title',
                                                                 'url_name', 'parent_id')
    permission_dict = {}
    for i in all_permissions:
        if i.get('menu_id'):
            permission_dict[i['id']] = i
            i['children'] = []
    for k in all_permissions:
        pid = k.get('parent_id')
        if pid:
            permission_dict[pid]['children'].append(k)
    return render(request, 'rbac/menu_list.html', {'all_menus': all_menus,
                                                   'permission_dict': permission_dict,
                                                   'mid': mid,
                                                   })


# 菜单添加和编辑
class MenuForm(forms.ModelForm):
    class Meta:
        model = models.Menu
        fields = '__all__'
        # exclude = ['permissions', ]
        widgets = {
            'title': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.widgets.RadioSelect(choices=[[i[0], mark_safe(i[1])] for i in icon_list])
        }
        labels = {
            'title': '标题',
            'icon': '图标',
            'weight': '优先级',
        }


# 菜单添加和编辑
def menu_add_edit(request, mid=None):
    menu_obj = models.Menu.objects.filter(id=mid).first()
    if request.method == 'GET':
        form_obj = MenuForm(instance=menu_obj)
        return render(request, 'rbac/form.html', {'form_obj': form_obj})
    else:
        form_obj = MenuForm(request.POST, instance=menu_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('rbac:menu_list')
        else:
            return render(request, 'rbac/form.html', {'form_obj': form_obj})


# 菜单删除
def menu_del(request, mid):
    models.Menu.objects.filter(id=mid).delete()
    return redirect('rbac:menu_list')


# 权限添加和编辑
class PermissionForm(forms.ModelForm):
    class Meta:
        model = models.Permission
        fields = '__all__'
        labels = {
            'title': '名称',
            'menu': '一级菜单',
            'parent': '二级菜单',
            'url_name': 'URL别名',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


def permission(request, pid=None):
    permission_obj = models.Permission.objects.filter(id=pid).first()
    if request.method == 'GET':
        form_obj = PermissionForm(instance=permission_obj)
        return render(request, 'rbac/form.html', {'form_obj': form_obj})
    else:
        form_obj = PermissionForm(request.POST, instance=permission_obj)
        if form_obj.is_valid():
            form_obj.save()
            redirect('rbac:menu_list')
        else:
            return render(request, 'rbac/form.html', {'form_obj': form_obj})


def permission_del(request, pid):
    models.Permission.objects.filter(id=pid).delete()
    return redirect('rbac:menu_list')


# 批量操作
def multi_permissions(request, pid=None):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')

    # 更新和编辑
    Form_Set = modelformset_factory(models.Permission, MultiPermissionForm, extra=0)

    # 添加
    Add_Form_Set = formset_factory(MultiPermissionForm, extra=0)

    # 查出数据库中所有的URL权限
    permissions = models.Permission.objects.all()

    # 获取应用中的所有URL
    url_dict = all_url(ignore_namespace_list=['admin', ])

    # 获取数据库中所有URL的别名
    permission_url_name = set([i.url_name for i in permissions])

    # 获取应用的所有别名
    url_dict_name = set(url_dict.keys())
    add_error_message = ''
    if request.method == 'POST' and post_type == 'add':
        add_formset = Add_Form_Set(request.POST)
        if add_formset.is_valid():

            obj_list = [models.Permission(**i) for i in add_formset.cleaned_data]
            new_permissions_obj = models.Permission.objects.bulk_create(obj_list)
            for i in new_permissions_obj:
                permission_url_name.add(i.url_name)
        else:
            add_error_message = add_formset.errors
    add_name = url_dict_name - permission_url_name
    add_formset = Add_Form_Set(initial=[msg for name, msg in url_dict.items() if name in add_name])

    del_name = permission_url_name - url_dict_name
    del_formset = Form_Set(queryset=models.Permission.objects.filter(url_name__in=del_name))

    edit_name = permission_url_name & url_dict_name
    edit_formset = Form_Set(queryset=models.Permission.objects.filter(url_name__in=edit_name))

    if request.method == 'POST' and post_type == 'edit':
        edit_formset = Form_Set(request.POST)
        if edit_formset.is_valid():
            edit_formset.save()
            edit_formset = Form_Set(queryset=models.Permission.objects.filter(url_name__in=edit_name))

    return render(request,
                  'rbac/multi_permissions.html',
                  {
                    'add_formset': add_formset,
                    'del_formset': del_formset,
                    'edit_formset': edit_formset,
                    'add_error_message': add_error_message,
                   }
                  )


# 权限分配
def distribute_permissions(request):
    """
    权限分配
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')
    if request.method == 'POST' and request.POST.get('postType') == 'role':
        user = UserInfo.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = models.Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))


    # 所有用户
    all_user_list = UserInfo.objects.all()

    # 用户拥有的角色
    user_has_roles = UserInfo.objects.filter(id=uid).values('id', 'roles')
    user_has_roles_dict = {item['roles']: None for item in user_has_roles}

    # 所有角色
    all_roles_list = models.Role.objects.all()
    if rid:
        role_has_permissions = models.Role.objects.filter(id=rid).values('id', 'permissions')
        #[{'id':1,'permissions':2},{'id':1,'permissions':4}]
    elif uid and not rid:
        user = UserInfo.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.values('id', 'permissions')
    else:
        role_has_permissions = []
    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    all_menu_list = []
    menu_queryset = models.Menu.objects.values('id', 'title')
    menu_dict = {}
    for i in menu_queryset:
        i['children'] = []
        menu_dict[i['id']] = i
        all_menu_list.append(i)
    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other

    sec_permissions = models.Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')
    sec_permissions_dict = {}
    for i in sec_permissions:
        i['children'] = []
        smid = i['id']  # 二级菜单id
        fmid = i['menu_id']   # 一级菜单id
        sec_permissions_dict[smid] = i
        menu_dict[fmid]['children'].append(i)

    root_permissions = models.Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')
    for i in root_permissions:
        pid = i['parent_id']  # 从属的二级菜单id
        if not pid:
            menu_dict[None]['children'].append(i)
            continue
        sec_permissions_dict[pid]['children'].append(i)

    return render(
        request,
        'rbac/distribute_permission.html',
        {
            'uid': uid,
            'rid': rid,
            'all_roles_list': all_roles_list,
            'all_user_list': all_user_list,
            'all_menu_list': all_menu_list,
            'user_has_roles_dict': user_has_roles_dict,
            'role_has_permissions_dict': role_has_permissions_dict,

        }
    )