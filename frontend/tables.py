from django.contrib.auth.models import User 

from django_datatables_view.base_datatable_view import BaseDatatableView
from .models import *


class QueryData(BaseDatatableView):
    model = Query
    columns = ['id', 'input', 'updated_at', 'interval', 'counter', 'status', 'capture']
    order_columns = ['id', 'input', 'updated_at', 'interval', 'counter', 'status', 'capture']
    max_display_length = 100

    def get_initial_queryset(self):
        user = self.request.user
        groups = self.request.user.groups.all()
        group_member = User.objects.filter(groups__in=groups).distinct()
        qs = None
        if user.is_authenticated():
            qs = Query.objects.filter(restriction=2) \
                |Query.objects.filter(restriction=1, registered_by__in=group_member) \
                |Query.objects.filter(restriction=0)
        else:
            qs = Query.objects.filter(restriction=2)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/query/{0}">{0}</a>'.format(row.id)
        elif column == 'registered_by':
            r = None
            if row.registered_by:
                r = row.registered_by.username
            return '{0}'.format(r)
        elif column == 'capture':
            job = Job.objects.filter(query=row.id).order_by("-id")
            c = None
            if job:
                capture = job[0].capture
                if capture:
                    path = None
                    if capture.path:
                        path = capture.path.encode("utf-8")
                    c = '<a class="colorbox" href="/{0}"><img src="data:image/png;base64,{1}"></a>'.format(path, capture.b64thumb)
            return c
        elif column == 'status':
            s = None
            job = Job.objects.filter(query=row.id).order_by("-id")
            if job:
                page = job[0].page
                if page:
                    s = page.http_status
            return '{0}'.format(s)
        else:
            return super(QueryData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(input__iregex=search) \
                | qs.filter(registered_by__username__iregex=search) \
                | qs.filter(restriction__iregex=search) \
                | qs.filter(interval__iregex=search) \
                | qs.filter(counter__iregex=search) \
                | qs.filter(created_at__iregex=search) \
                | qs.filter(updated_at__iregex=search)
        return qs.distinct()


class JobData(BaseDatatableView):
    model = Job
    columns = ['id', 'created_at', 'query', 'status', 'capture']
    order_columns = ['id', 'created_at', 'query', 'status', 'capture']
    max_display_length = 100

    def get_initial_queryset(self):
        user = self.request.user
        groups = self.request.user.groups.all()
        group_member = User.objects.filter(groups__in=groups).distinct()
        qs = None
        if user.is_authenticated():
            qs = Job.objects.filter(query__restriction=2) \
                |Job.objects.filter(query__restriction=1, query__registered_by__in=group_member) \
                |Job.objects.filter(query__restriction=0)
        else:
            qs = Job.objects.filter(query__restriction=2)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            a = '<a class="btn btn-primary" href="/job/{0}">{0}</a>'.format(row.id)
            if row.page:
                if row.page.analysis:
                    if row.page.analysis.rule.all():
                        a += '<i class="fa fa-warning fa-lg" title="signature matched">'
            return a
        elif column == 'query':
            i = None
            if row.query:
                i = row.query.input.encode("utf-8")
            return '{0}'.format(i)
        elif column == 'capture':
            c = None
            if row.capture:
                path = None
                if row.capture.path:
                    path = row.capture.path.encode("utf-8")
                c = '<a class="colorbox" href="/{0}"><img src="data:image/png;base64,{1}"></a>'.format(path, row.capture.b64thumb)
            return c
        else:
            return super(JobData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(query__input__iregex=search) \
                | qs.filter(status__iregex=search) \
                | qs.filter(created_at__iregex=search)
        return qs.distinct()


class DNSData(BaseDatatableView):
    model = DNSRecord
    #columns = ['id', 'first_seen', 'query', 'a', 'txt']
    columns = ['id', 'first_seen', 'query', 'resolver', 'a']
    order_columns = ['id', 'first_seen', 'query', 'resolver', 'a']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/dns/{0}">{0}</a>'.format(row.id)
        elif column == 'a':
            td = ""
            for i in row.a.all():
                td += i.ip + "<br>"
            return '{0}'.format(td)
        elif column == 'resolver':
            td = ""
            for i in row.resolver.all():
                td += i.ip + "<br>"
            return '{0}'.format(td)
        else:
            return super(DNSData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(query__iregex=search) \
                | qs.filter(a__ip__iregex=search) \
                | qs.filter(resolver__ip__iregex=search) \
                | qs.filter(first_seen__iregex=search)
        return qs.distinct()


class DomainWhoisData(BaseDatatableView):
    model = Domain_Whois
    columns = ['id', 'creation_date', 'updated_date', 'domain', 'contact']
    order_columns = ['id', 'creation_date', 'updated_date', 'domain', 'contact']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/whois_domain/{0}">{0}</a>'.format(row.id)
        elif column == 'domain':
            i = None
            n = None
            if row.domain:
                i = row.domain.id
                n = row.domain.name.encode("utf-8")
            return '<a href="/domain/{0}">{1}</a>'.format(i, n)
        elif column == 'contact':
            t = '<table class="table display" cellspacing="0" width="100%">'
            for c in row.contact.all():
                type = ""
                if c.type:
                    type = c.type
                name = ""
                if c.person:
                    if c.person.email:
                        org = c.person.email
                t += '<tr>'
                t += '<td>' + type + '</td>'
                t += '<td>' + org + '</td>'
                t += '</tr>'
            t += '</table>'
            return '{0}'.format(t)
        else:
            return super(DomainWhoisData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(domain__name__iregex=search) \
                | qs.filter(contact__person__organization__iregex=search) \
                | qs.filter(creation_date__iregex=search) \
                | qs.filter(updated_date__iregex=search)
        return qs.distinct()


class IPWhoisData(BaseDatatableView):
    model = IP_Whois
    columns = ['id', 'creation_date', 'updated_date', 'ip', 'country', 'description']
    order_columns = ['id', 'creation_date', 'updated_date', 'ip', 'country', 'description']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/whois_ip/{0}">{0}</a>'.format(row.id)
        elif column == 'ip':
            i = None
            if row.ip:
                i = row.ip.ip
            return '{0}'.format(i)
        elif column == 'domain':
            i = None
            n = None
            if row.domain:
                i = row.domain.id
                n = row.domain.name
            return '<a href="/domain/{0}">{1}</a>'.format(i, n)
        elif column == 'country':
            td = None
            if row.country:
                td = '<span class="flag-icon flag-icon-{0}" title="{0}" style="border:solid thin lightgrey"></span>'.format(row.country.lower())
            return '{0}'.format(td)
        else:
            return super(IPWhoisData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(ip__ip__iregex=search) \
                | qs.filter(country__iregex=search) \
                | qs.filter(description__iregex=search) \
                | qs.filter(creation_date__iregex=search) \
                | qs.filter(updated_date__iregex=search)
        return qs.distinct()


class HostInfoData(BaseDatatableView):
    model = Host_Info
    columns = ['id', 'first_seen', 'last_seen', 'hostname', 'ip_whois', 'domain_dns', 'domain_whois']
    order_columns = ['id', 'first_seen', 'last_seen', 'hostname', 'host_dns', 'domain_dns', 'domain_whois']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" >{0}</a>'.format(row.id)
        elif column == 'hostname':
            n = None
            if row.hostname:
                n = row.hostname.name.encode("utf-8")
            return '{0}'.format(n)
        elif column == 'ip_whois':
            td = ""
            for i in row.ip_whois.all():
                td += '<a href="/whois_ip/{0}">{1}</a><br>'.format(i.id, i.ip)
            return '{0}'.format(td)
        elif column == 'domain_dns':
            #d = None
            i = None
            n = None
            if row.domain_dns:
                #d = row.domain_dns.serialized
                i = row.domain_dns.id
                n = row.domain_dns.query.encode("utf-8")
            #return '{0}'.format(d)
            return '<a href="/dns/{0}">{1}</a>'.format(i, n)
        elif column == 'domain_whois':
            i = None
            n = None
            if row.domain_whois:
                i = row.domain_whois.id
                n = row.domain_whois.domain.name.encode("utf-8")
            return '<a href="/whois_domain/{0}">{1}</a>'.format(i, n)
        else:
            return super(HostInfoData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(hostname__name__iregex=search) \
                | qs.filter(ip_whois__ip__ip__iregex=search) \
                | qs.filter(domain_dns__serialized__iregex=search) \
                | qs.filter(domain_whois__domain__name__iregex=search) \
                | qs.filter(first_seen__iregex=search) \
                | qs.filter(last_seen__iregex=search)
        return qs.distinct()



class UAData(BaseDatatableView):
    model = UserAgent
    columns = ['id', 'name', 'strings']
    order_columns = ['id', 'name', 'strings']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary">{0}</a>'.format(row.id)
        else:
            return super(UAData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(name__iregex=search) \
                | qs.filter(strings__iregex=search) \
                | qs.filter(created_at__iregex=search)
        return qs.distinct()

