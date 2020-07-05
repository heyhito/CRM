from django.shortcuts import (render, redirect,HttpResponse)
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.views import View
from django.forms.models import modelformset_factory

from sales.utils.paging import Mypaging
from sales import models
from sales.myforms import (CustomerForm,ConsultRecordForm,EnrollRecordForm,CourseRecordForm,StudyRecordForm)
from sales.models import enroll_status_choices


# 公私户信息展示
class CustomersView(View):
    def get(self, request):
        get_path = request.path  # 获取请求路径
        # 公户请求
        if get_path == reverse('customer'):  # 查找销售为None的客户
            tag = '1'
            customer_list = models.Customer.objects.filter(consultant__isnull=True)
        else:
            # 私户请求
            tag = '2'
            user_obj = request.user_obj
            customer_list = models.Customer.objects.filter(consultant=user_obj)
        # 当前页
        search_conditon = request.GET.copy()  # 获取搜索条件
        # QueryDict<{'search_field':'name__contains','kw':'钢铁侠'}>
        """
        将request.get对象改成可修改的，因为queryDict对象默认是immutable，需要通过调用__copy__方法，该方法设置的是mutable=True
        """
        page_num = request.GET.get('page')  # 当前页码
        kw = request.GET.get('kw')  # 查询关键字
        search_field = request.GET.get('search_field')  # 选择查询的字段
        """
        判断是搜索还是客户信息展示
        """
        if kw:
            kw = kw.strip()
            if search_field == 'sex__contains':
                if kw == '女':
                    kw = 'female'
                    q_obj = Q()
                    q_obj.children.append((search_field, kw))
                    customer_list = customer_list.filter(q_obj)
                else:
                    kw = 'female'
                    q_obj = Q()
                    q_obj.children.append((search_field, kw))
                    customer_list = customer_list.filter().exclude(q_obj)
            elif search_field == 'status__contains':
                for i in enroll_status_choices:
                    if kw == i[1]:
                        kw = i[0]
                q_obj = Q()
                q_obj.children.append((search_field, kw))
                customer_list = customer_list.filter(q_obj)
            else:
                q_obj = Q()
                q_obj.children.append((search_field, kw))
                customer_list = customer_list.filter(q_obj)  # name__contains = kw
        else:
            customer_list = customer_list
        page_count = customer_list.count()
        per_page_show = settings.PER_PAGE_SHOW
        show_page = settings.SHOW_PAGE
        base_url = request.path
        paging_obj = Mypaging(page_num, page_count, per_page_show, show_page, base_url, search_conditon)
        paging_html = paging_obj.page_html()
        customer = customer_list.reverse()[paging_obj.start_page:paging_obj.end_page]
        return render(request, 'saleshtml/customers.html', {'customer': customer, 'paging_html': paging_html,'tag':tag})

    def post(self, request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cid')

        if hasattr(self, action):
            ret = getattr(self, action)(request, cids)
            if ret:
                return ret
        return redirect(request.path)

    def reverse_gs(self, request, cids):
        """
        公共用户转私有用户
        :param request:
        :param customer:
        :return:
        """
        customer = models.Customer.objects.filter(id__in=cids,consultant__isnull=True)
        if customer.count() != len(cids):
            null_customer = models.Customer.objects.filter(id__in=cids,consultant__isnull=False)
            lis = []
            for obj in null_customer:
                lis.append(obj.name)
            alert_html = '<div class="alert alert-danger" role="alert">{0}已有销售<a href="{1}" class="btn btn-primary pull-right">返回</a></div>'.format(lis,request.path)
            return render(request,'saleshtml/customers.html',{'alert_html':alert_html})
        customer.update(consultant_id=request.session.get('user_id'))

    def reverse_sg(self, request, cids):
        """
        私有用户转公共用户
        :param :
        :return:
        """
        customer = models.Customer.objects.filter(id__in=cids,consultant=request.user_obj)
        customer.update(consultant=None)


# 客户添加和编辑
def add_edit_customer(request, cid=None):
    """
    # 客户添加和编辑
    :param request:
    :param cid:客户id
    :return:
    """
    label = '编辑客户' if cid else '添加客户'
    customer_obj = models.Customer.objects.filter(pk=cid).first()
    if request.method == 'GET':
        customer_form = CustomerForm(instance=customer_obj)
        return render(request,'saleshtml/form.html', {'customer_form': customer_form, 'label': label})
    else:
        customer_form = CustomerForm(request.POST, instance=customer_obj)
        if customer_form.is_valid():
            customer_form.save()
            redirect_path = request.GET.get('next')
            if redirect_path is not None:
                return redirect(redirect_path)
            else:
                return redirect('customer')
        else:
            return render(request, 'saleshtml/form.html', {'customer_form': customer_form,'label':label})


# 客户跟进记录信息展示
class ConsultRecordView(View):
    def get(self,request):
        cid = request.GET.get('cid')
        # 如果存在cid，那么找的是单个客户的跟进记录
        if cid:
            consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj,delete_status=False,customer_id=cid)
        else:
            consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj,delete_status=False)
        # 分页和搜索
        search_conditon = request.GET.copy()
        page_num = request.GET.get('page')
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field,kw))
            consult_list = consult_list.filter(q_obj)
        else:
            consult_list = consult_list
        page_count = consult_list.count()
        per_page_show = settings.PER_PAGE_SHOW
        show_page = settings.SHOW_PAGE
        base_url = request.path
        paging_obj = Mypaging(page_num, page_count, per_page_show, show_page, base_url, search_conditon)
        paging_html = paging_obj.page_html()
        consult_obj = consult_list.reverse()[paging_obj.start_page:paging_obj.end_page]
        return render(request, 'saleshtml/consultrecord.html', {'paging_html': paging_html,
                                                              'consult_obj': consult_obj})
    def post(self,request):
        action = request.POST.get('action')
        cid = request.POST.getlist('cid')
        if hasattr(self, action):
            getattr(self, action)(cid)
        return redirect(request.path)
    # 客户跟进记录删除
    def delete_consultrecord(sels,cid):
        models.ConsultRecord.objects.filter(id__in=cid).update(delete_status=True)


# 客户跟进记录添加和编辑
def add_edit_consultrecord(request,cid=None):
    tag = '1'
    label = '编辑客户跟踪记录' if cid else '添加客户跟踪记录'
    customer_obj = models.ConsultRecord.objects.filter(id=cid).first()
    if request.method == 'GET':
        customer_form = ConsultRecordForm(request,instance=customer_obj)
        return render(request, 'saleshtml/form.html',
                      {'customer_form': customer_form, 'label': label, 'tag': tag})
    else:
        customer_form = ConsultRecordForm(request, request.POST, instance=customer_obj)
        next_url = request.GET.get('next')
        if not next_url:
            next_url = 'consultrecord'
        if customer_form.is_valid():
            customer_form.save()
            return redirect(next_url)
        else:
            return render(request, 'saleshtml/form.html', {'customer_form':customer_form, 'label': label})


# 报名信息表展示
class EnrollmentView(View):

    def get(self,request):
        enrolls = models.Enrollment.objects.filter(customer__consultant=request.user_obj,delete_status=False)
        search_conditon = request.GET.copy()
        page_num = request.GET.get('page')
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kw))
            consult_list = enrolls.filter(q_obj)
        else:
            consult_list = enrolls
        page_count = consult_list.count()
        per_page_show = settings.PER_PAGE_SHOW
        show_page = settings.SHOW_PAGE
        base_url = request.path
        paging_obj = Mypaging(page_num, page_count, per_page_show, show_page, base_url, search_conditon)
        paging_html = paging_obj.page_html()
        consult_obj = consult_list.reverse()[paging_obj.start_page:paging_obj.end_page]
        return render(request, 'saleshtml/enrollment.html', {'enrolls': enrolls, 'paging_html': paging_html,'consult_obj': consult_obj})

    def post(self,request):
        cid = request.POST.get('cid')
        action = request.POST.get('action')
        if hasattr(self, action):
            getattr(self, action)(cid)
        return redirect(request.path)

    def delete_consultrecord(self, cid):
        models.Enrollment.objects.filter(id__in=cid).update(delete_status=True)



# 报名表信息添加和编辑
class Add_Edit_EnrollRecord(View):
    def get(self,request,cid=None):
        label = '编辑报名信息' if cid else '添加报名信息'
        customer_obj = models.Enrollment.objects.filter(id=cid).first()
        customer_form = EnrollRecordForm(request, instance=customer_obj)
        return render(request, 'saleshtml/form.html', {'customer_form': customer_form, 'label': label})
    def post(self,request,cid=None):
        label = '编辑报名信息' if cid else '添加报名信息'
        customer_obj = models.Enrollment.objects.filter(id=cid).first()
        next_url = request.GET.get('next')
        if not next_url:
            next_url = 'enrollment'
        customer_form = EnrollRecordForm(request, request.POST, instance=customer_obj)
        if customer_form.is_valid():
            customer_form.save()
            return redirect(next_url)
        else:
            return render(request, 'saleshtml/form.html', {'customer_form': customer_form, 'label': label})


# 课程记录展示表
class CourseRecordView(View):
    def get(self, request):
        course_record = models.CourseRecord.objects.all()
        search_conditon = request.GET.copy()
        page_num = request.GET.get('page')
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kw))
            course_record_list = course_record.filter(q_obj)
        else:
            course_record_list = course_record
        page_count = course_record_list.count()
        per_page_show = settings.PER_PAGE_SHOW
        show_page = settings.SHOW_PAGE
        base_url = request.path
        paging_obj = Mypaging(page_num, page_count, per_page_show, show_page, base_url, search_conditon)
        paging_html = paging_obj.page_html()
        course_obj = course_record_list.reverse()[paging_obj.start_page:paging_obj.end_page]
        return render(request, 'saleshtml/course_record.html',
                      {'course_obj': course_obj, 'paging_html': paging_html})

    def post(self, request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cid')
        if hasattr(self, action):
            getattr(self, action)(cids)
        return redirect(request.path)

    # 删除
    def delete_consultrecord(self, cids):
        models.CourseRecord.objects.filter(id__in=cids).delete()

    # 生成学习记录
    def study_record(self, cids):
        # 先找到当前被选中的课程记录，通过课程记录表里的班级找到，通过当前班级找到该班级
        # 学习中的客户，然后生成学习记录
        obj_lis = []
        for cid in cids:
            course_record_obj = models.CourseRecord.objects.filter(id=cid).first()
            student_obj = course_record_obj.re_class.customer_set.filter(status='studying').first()
            obj = models.StudyRecord(
                course_record_id=cid,
                student=student_obj
            )
            obj_lis.append(obj)
        models.StudyRecord.objects.bulk_create(obj_lis)


# 课程记录的添加和编辑
class Add_Edit_CourseRecord(View):
    def get(self,request,cid=None):
        label = '编辑课程记录' if cid else '添加课程记录'
        customer_obj = models.CourseRecord.objects.filter(id=cid).first()
        customer_form = CourseRecordForm(request,instance=customer_obj)
        return render(request, 'saleshtml/form.html',
                      {'customer_form': customer_form,'label': label})

    def post(self,request,cid=None):
        label = '编辑课程记录' if cid else '添加课程记录'
        customer_obj = models.CourseRecord.objects.filter(id=cid).first()
        next_url = request.GET.get('next')
        if not next_url:
            next_url = 'course_record'
        customer_form = CourseRecordForm(request,request.POST,instance=customer_obj)
        if customer_form.is_valid():
            customer_form.save()
            return redirect(next_url)
        else:
            return render(request, 'saleshtml/form.html',
                          {'customer_form': customer_form, 'label': label})


# 学习记录展示
class StudyRecordView(View):
    def get(self, request, cid=None):
        # 目的：通过课程记录找到学习该课程的所有客户的学习记录
        # 因为课程记录和客户表没有关系，但课程记录通过外键关联了班级表，而客户表通过外键关联了班级表，
        # 因此可以通过课程记录正向查找，找到该课程的班级，再通过该班级反向查询到在该班级学习的所有客户，
        # 找到学习该课程的客户后，将其放到学习记录表的student字段中，这样就生成了该学生学习该课程的学习记录。

        # 拿到了课程记录的id，通过该课程记录的id找到该课程的学习记录
        # study_record = models.StudyRecord.objects.filter(course_record_id=cid)
        # modelformset_factory会将表里面的所有记录根据所给的modelform去生成多条数据的页面效果，
        # 类似于modelform，只不过modelform是生成单条记录。
        formset = modelformset_factory(model=models.StudyRecord, form=StudyRecordForm, extra=0)
        study_record = models.StudyRecord.objects.filter(course_record_id=cid)
        formset = formset(queryset=study_record)
        # 生成的记录会将表里的所有数据生成在页面，因此需要通过其他方法进行指定生成数据
        return render(request,'saleshtml/studyrecord.html', {'formset': formset})

    def post(self, request, cid):
        formset = modelformset_factory(model=models.StudyRecord, form=StudyRecordForm, extra=0)
        formset = formset(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(request.path)
        else:
            return render(request, 'saleshtml/studyrecord.html', {'formset': formset})