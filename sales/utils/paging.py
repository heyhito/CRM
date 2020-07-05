from django.utils.safestring import mark_safe

class Mypaging():
    def __init__(self,page_num,page_count,per_page_show,show_page,base_url,search_conditon = None):
        """

        :param page_num: 当前页
        :param page_count: 数据总数
        :param per_page_show: 每页显示的数据量
        :param show_page: 每页显示的页码数
        :param base_url: 基础路径
        :param search_conditon: QueryDict对象
        """
        self.search_conditon = search_conditon
        self.per_page_show = per_page_show
        self.page_count = page_count
        self.base_url = base_url
        try:
            page_num = int(page_num)
        except Exception:
            page_num = 1
        self.page_num = page_num
    # 总页码数
        quotient,remainder = divmod(page_count, self.per_page_show)
        if remainder:
            per_page_count = quotient + 1
        else:
            per_page_count = quotient
        self.per_page_count = per_page_count
        if self.page_num <= 0:
            self.page_num = 1
        # elif self.page_num > per_page_count:
        #     self.page_num = per_page_count

        # 页码数
        middle_page = show_page//2 #-->2
        if self.page_num - middle_page <= 0:
            per_start_page = 1
            per_end_page = show_page+1
        elif self.page_num + middle_page > per_page_count:
            per_start_page = per_page_count - show_page + 1 #26-5=22
            per_end_page = per_page_count + 1           #27 -->[22:27]
        else:
            per_start_page = self.page_num - middle_page
            per_end_page = self.page_num + middle_page + 1
        """
        如果页码应该显示的页数小于页码设置显示的页数，范围就应该为该页码应该显示的页数,
        即251条数据，每页显示十条，每页的页码数设置为5页，则总的页码数应该为26页,
        当搜索的结果的总数据整除每页显示十条的结果，小于设置的页码数5页时，就应该讲应该显示的页码数的范围编程[1,搜索结果的总数据整除每页显示十条数据的结果]
        """
        if per_page_count < show_page:
            per_start_page = 1
            per_end_page = per_page_count + 1
        self.per_start_page = per_start_page
        self.per_end_page = per_end_page
    @property
    def start_page(self):
        """
        每页显示数据的内容
        :return: 每页数据的起始id
        """
        return (self.page_num - 1) * self.per_page_show

    @property
    def end_page(self):
        """
        每页显示数据的内容
        :return: 每页数据的末尾id
        """
        return self.page_num * self.per_page_show

    def page_html(self):
        """
        生成页码标签
        :return: 页码标签
        """
        per_page_num_range = range(self.per_start_page,self.per_end_page)
        base_html = ''
        previous_html = '<nav aria-label="Page navigation"><ul class="pagination">'
        base_html += previous_html
        self.search_conditon['page'] = 1
        first_html = '<li><a href="{0}?{1}" aria-label="Previous"><span aria-hidden="true">首页</span></a></li>'\
            .format(self.base_url,self.search_conditon.urlencode())
        base_html += first_html
        if self.page_num <= 1:
            up_page = '<li class="disabled"><a href="javascript:void(0)" aria-label="Previous">' \
                      '<span aria-hidden="true">&laquo;</span></a></li>'
        else:
            self.search_conditon['page'] = self.page_num - 1
            up_page = '<li><a href="{0}?{1}" aria-label="Previous">' \
                      '<span aria-hidden="true">&laquo;</span></a></li>'.format(self.base_url,self.search_conditon.urlencode())
            # search_conditon.urlencode()——>search_field=name__contains&kw=钢铁侠
        base_html += up_page
        for i in per_page_num_range:
            if i == self.page_num:
                self.search_conditon['page'] = i
                base_html += '<li class="active"><a href="{0}?{2}">{1}</a></li>'.format(self.base_url,i,self.search_conditon.urlencode())
            else:
                self.search_conditon['page'] = i
                base_html += '<li><a href="{0}?{2}">{1}</a></li>'.format(self.base_url,i,self.search_conditon.urlencode())
        if self.page_num >= self.per_page_count:
            down_page = '<li class="disabled"><a href="javascript:void(0)" aria-label="Previous">' \
                      '<span aria-hidden="true">&raquo;</span></a></li>'
        else:
            self.search_conditon['page'] = self.page_num + 1
            down_page = '<li><a href="{0}?{1}" aria-label="Previous">' \
                        '<span aria-hidden="true">&raquo;</span></a></li>'.format(self.base_url,self.search_conditon.urlencode())
        base_html += down_page
        self.search_conditon['page'] = self.per_page_count
        last_htme ='<li><a href="{0}?{1}" aria-label="Next"><span aria-hidden="true">尾页</span></a></li>'.format(self.base_url, self.search_conditon.urlencode())
        base_html += last_htme
        end_html = '</ul></nav>'
        base_html += end_html

        return mark_safe(base_html)
