from django import forms
from rbac import models


# 批量操作的form
class MultiPermissionForm(forms.ModelForm):
    class Meta:
        model = models.Permission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'title':
                field.widget.attrs.update({'placeholder': '标题不能为空'})

        self.fields['parent'].choices = [(None,'------')] + list(
            models.Permission.objects.filter(parent__isnull=True).exclude(
                menu__isnull=True).values_list('id', 'title'))


    def clean(self):
        menu = self.cleaned_data.get('menu')
        parent = self.cleaned_data.get('parent')
        if menu and parent:
            raise forms.ValidationError('菜单和根权限同时只能选择一个')
        else:
            return self.cleaned_data