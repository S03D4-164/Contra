from django.shortcuts import render_to_response
from django.template import RequestContext

from django_datatables_view.base_datatable_view import BaseDatatableView
from .models import *


class QueryData(BaseDatatableView):
    model = Query
    columns = ['id', 'input', 'updated_at', 'registered_by', 'restriction', 'interval', 'counter']
    order_columns = ['id', 'input', 'updated_at', 'registered_by', 'restriction', 'interval', 'counter']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/query/{0}">{0}</a>'.format(row.id)
        elif column == 'registered_by':
            return '{0}'.format(row.registered_by.username)
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

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/job/{0}">{0}</a>'.format(row.id)
        elif column == 'query':
            return '{0}'.format(row.query.input)
        elif column == 'capture':
            c = None
            if row.capture:
                c = '<a class="colorbox" href="/{0}"><img src="data:image/png;base64,{1}"></a>'.format(row.capture.path, row.capture.b64thumb)
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
    columns = ['id', 'first_seen', 'query', 'a', 'txt']
    order_columns = ['id', 'first_seen', 'query', 'a', 'txt']
    max_display_length = 100

    def render_column(self, row, column):
        if column == 'id':
            return '<a class="btn btn-primary" href="/dns/{0}">{0}</a>'.format(row.id)
        elif column == 'a':
            td = ""
            for i in row.a.all():
                td += i.ip + "<br>"
            return '{0}'.format(td)
        else:
            return super(DNSData, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(query__iregex=search) \
                | qs.filter(a__ip__iregex=search) \
                | qs.filter(txt__iregex=search) \
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
            return '<a href="/domain/{0}">{1}</a>'.format(row.domain.id,row.domain.name)
        elif column == 'contact':
            t = '<table class="table display" cellspacing="0" width="100%">'
            for c in row.contact.all():
                t += '<tr>'
                t += '<td>' + c.type + '</td>'
                t += '<td>' + c.person.organization + '</td>'
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
            return '{0}'.format(row.ip.ip)
        elif column == 'domain':
            return '<a href="/domain/{0}">{1}</a>'.format(row.domain.id,row.domain.name)
        elif column == 'country':
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
            return '{0}'.format(row.hostname.name)
        elif column == 'ip_whois':
            td = ""
            for i in row.ip_whois.all():
                td += '<a href="/whois_ip/{0}">{1}</a><br>'.format(i.id, i.ip)
            return '{0}'.format(td)
        elif column == 'domain_dns':
            return '{0}'.format(row.domain_dns.serialized)
        elif column == 'domain_whois':
            return '<a href="/whois_domain/{0}">{1}</a>'.format(row.domain_whois.id, row.domain_whois.domain.name)
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
    columns = ['id', 'created_at', 'name', 'strings']
    order_columns = ['id', 'created_at', 'name', 'strings']
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

