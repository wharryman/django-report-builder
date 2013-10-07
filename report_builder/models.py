from itertools import groupby
import functools
import operator
from collections import defaultdict
import numbers

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db import models
from django.db.models import Avg, Min, Max, Count, Sum
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible

from report_builder.unique_slugify import unique_slugify
from report_builder.utils import get_model_from_path_string
from dateutil import parser
from django.db import connection

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

@python_2_unicode_compatible
class Report(models.Model):
    """ A saved report with queryset and descriptive fields
    """
    def _get_allowed_models():
        models = ContentType.objects.all()
        if getattr(settings, 'REPORT_BUILDER_INCLUDE', False):
            models = models.filter(name__in=settings.REPORT_BUILDER_INCLUDE)
        if getattr(settings, 'REPORT_BUILDER_EXCLUDE', False):
            models = models.exclude(name__in=settings.REPORT_BUILDER_EXCLUDE)
        return models
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(verbose_name="Short Name")
    description = models.TextField(blank=True)
    root_model = models.ForeignKey(ContentType, limit_choices_to={'pk__in':_get_allowed_models})
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)
    user_created = models.ForeignKey(AUTH_USER_MODEL, editable=False, blank=True, null=True)
    user_modified = models.ForeignKey(AUTH_USER_MODEL, editable=False, blank=True, null=True, related_name="report_modified_set")
    distinct = models.BooleanField(default=True)
    starred = models.ManyToManyField(AUTH_USER_MODEL, blank=True,
                                     help_text="These users have starred this report for easy reference.",
                                     related_name="report_starred_set")
    category = models.ForeignKey('Report_Category', blank=True, null=True, default=None)
    read_only = models.BooleanField(default=False)
    #TODO: implement logic that restricts filter changes on a report that is read-only until that attrib is removed

    def __str__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        if not self.id:
            unique_slugify(self, self.name)
        super(Report, self).save(*args, **kwargs)

    def all_requirements_met(self):
        status = True
        for r in self.requiredfilter_set.all():
            status = status and r.requirements_met()
        return status

    def add_aggregates(self, queryset):
        for display_field in self.displayfield_set.filter(aggregate__isnull=False):
            if display_field.aggregate == "Avg":
                queryset = queryset.annotate(Avg(display_field.path + display_field.field))
            elif display_field.aggregate == "Max":
                queryset = queryset.annotate(Max(display_field.path + display_field.field))
            elif display_field.aggregate == "Min":
                queryset = queryset.annotate(Min(display_field.path + display_field.field))
            elif display_field.aggregate == "Count":
                queryset = queryset.annotate(Count(display_field.path + display_field.field))
            elif display_field.aggregate == "Sum":
                queryset = queryset.annotate(Sum(display_field.path + display_field.field))
        return queryset

    def get_query(self):
        report = self
        model_class = report.root_model.model_class()
        message= ""

        # Filters
        # NOTE: group all the filters together into one in order to avoid 
        # unnecessary joins
        filters = {}
        excludes = {}
        group = 1
        queries = []
        property_list = []
        custom_list = []
        field_list = []
        keys = []
        #for right now, let's get this working without props/customs

        #grouped Q objects
        for key, group in groupby(report.filterfield_set.all(), lambda x: x.grouping):
            field_list.append([x.process_filter() for x in group])
        print(field_list)
        query = Q()
        for c in field_list:
            q = Q()
            for q_obj in c:
                q.add( q_obj, Q.AND)
            query.add(q, Q.OR)

        objs = model_class.objects.filter(query)
        #grouping
        group_values = self.grouping_values()
        print("groupvalues", group_values)
        objs = objs.values(*group_values)
        objs = self.add_aggregates(objs)
        #sorting
        sort_values = self.sorting_values()
        print("sortvalues", sort_values)
        for g in group_values:
            if g not in sort_values:
                sort_values.append(g)
        objs = objs.order_by(*sort_values)
        if report.distinct:
            obj = objs.distinct()
        return objs

    def grouping_values(self):
        return [x.get_path_key() for x in self.displayfield_set.filter(group=True)]

    def sorting_values(self):
        sort = []
        for x in self.displayfield_set.filter(sort__gt=0).order_by('-sort'):
            if x.sort_reverse:
                sort.append("-"+x.get_path_key())
            else:
                sort.append(x.get_path_key())
        return sort



    
    @models.permalink
    def get_absolute_url(self):
        return ("report_update_view", [str(self.id)])
    
    def edit(self):
        return mark_safe('<a href="{0}"><img style="width: 26px; margin: -6px" src="{1}report_builder/img/edit.png"/></a>'.format(
            self.get_absolute_url(),
            getattr(settings, 'STATIC_URL', '/static/')   
        ))
    edit.allow_tags = True
    
    def download_xlsx(self):
        return mark_safe('<a href="{0}"><img style="width: 26px; margin: -6px" src="{1}report_builder/img/download.svg"/></a>'.format(
            reverse('report_builder.views.download_xlsx', args=[self.id]),
            getattr(settings, 'STATIC_URL', '/static/'),
        ))
    download_xlsx.short_description = "Download"
    download_xlsx.allow_tags = True
    

    def copy_report(self):
        return '<a href="{0}"><img style="width: 26px; margin: -6px" src="{1}report_builder/img/copy.svg"/></a>'.format(
            reverse('report_builder.views.create_copy', args=[self.id]),
            getattr(settings, 'STATIC_URL', '/static/'),
        )
    copy_report.short_description = "Copy"
    copy_report.allow_tags = True

    def check_report_display_field_positions(self):
        """ After report is saved, make sure positions are sane
        """
        for i, display_field in enumerate(self.displayfield_set.all()):
            if display_field.position != i+1:
                display_field.position = i+1
                display_field.save()

@python_2_unicode_compatible
class Report_Category(models.Model):
    """Used to classify reports presented to a user by a named type
    """

    name = models.CharField(max_length=50, unique=True)
    about = models.CharField(max_length=300, blank=True, default='')
    parent_cat = models.ForeignKey('self', blank=True, null=True, default=None)

    def __str__(self):
        return self.name

class Format(models.Model):
    """ A specifies a Python string format for e.g. `DisplayField`s. 
    """
    name = models.CharField(max_length=50, blank=True, default='')
    string = models.CharField(max_length=300, blank=True, default='', help_text='Python string format. Ex ${} would place a $ in front of the result.')

    def __unicode__(self):
        return self.name
    

@python_2_unicode_compatible
class DisplayField(models.Model):
    """ A display field to show in a report. Always belongs to a Report
    """
    report = models.ForeignKey(Report)
    path = models.CharField(max_length=2000, blank=True)
    path_verbose = models.CharField(max_length=2000, blank=True)
    field = models.CharField(max_length=2000)
    field_verbose = models.CharField(max_length=2000)
    name = models.CharField(max_length=2000)
    sort = models.IntegerField(blank=True, null=True)
    sort_reverse = models.BooleanField(verbose_name="Reverse")
    width = models.IntegerField(default=15)
    aggregate = models.CharField(
        max_length=5,
        choices = (
            ('Sum','Sum'),
            ('Count','Count'),
            ('Avg','Avg'),
            ('Max','Max'),
            ('Min','Min'),
        ),
        blank = True
    )
    position = models.PositiveSmallIntegerField(blank = True, null = True)
    total = models.BooleanField(default=False)
    group = models.BooleanField(default=False)
    display_format = models.ForeignKey(Format, blank=True, null=True)

    class Meta:
        ordering = ['position']
    
    def get_choices(self, model, field_name):
        try:
            model_field = model._meta.get_field_by_name(field_name)[0]
        except:
            model_field = None
        if model_field and model_field.choices:
            return model_field.choices

    @property
    def choices_dict(self):
        choices = self.choices
        choices_dict = {}
        if choices:
            for choice in choices:
                choices_dict.update({choice[0]: choice[1]})
        return choices_dict

    @property
    def choices(self):
        if self.pk:
            model = get_model_from_path_string(self.report.root_model.model_class(), self.path)
            return self.get_choices(model, self.field)

    def get_path_key(self):
        display_field_key = self.path+self.field
        display_field = self
        if display_field.aggregate == "Avg":
            display_field_key += '__avg'
        elif display_field.aggregate == "Max":
            display_field_key += '__max'
        elif display_field.aggregate == "Min":
            display_field_key += '__min'
        elif display_field.aggregate == "Count":
            display_field_key += '__count'
        elif display_field.aggregate == "Sum":
            display_field_key += '__sum'
        return display_field_key

    def format_value(self, value):
        "attempt to apply the DisplayField format to a value"
        
        if (value == None or self.display_format == None):
            return value
        if isinstance(value, numbers.Number):
            try:
                value = self.display_format.string.format(value)
                return float(value)
            except:
                print("cannot convert to Float")
                return value
        else:
            # Try to format the value, let it go without formatting for ValueErrors
            try:
                return self.display_format.string.format(value)
            except ValueError, AttributeError:
                print("cannot apply format")
                return value

    def __unicode__(self):
        return self.name
    
    def __str__(self):
        return self.name + " " + self.report.__str__()
        
@python_2_unicode_compatible
class FilterField(models.Model):
    """ A display field to show in a report. Always belongs to a Report
    """
    report = models.ForeignKey(Report)
    path = models.CharField(max_length=2000, blank=True)
    path_verbose = models.CharField(max_length=2000, blank=True)
    field = models.CharField(max_length=2000)
    field_verbose = models.CharField(max_length=2000)
    filter_type = models.CharField(
        max_length=20,
        choices = (
            ('exact','Equals'),
            ('iexact','Equals (case-insensitive)'),
            ('contains','Contains'),
            ('icontains','Contains (case-insensitive)'),
            ('in','in (comma seperated 1,2,3)'),
            ('gt','Greater than'),
            ('gte','Greater than equals'),
            ('lt','Less than'),
            ('lte','Less than equals'),
            ('startswith','Starts with'),
            ('istartswith','Starts with (case-insensitive)'),
            ('endswith','Ends with'),
            ('iendswith','Ends with  (case-insensitive)'),
            ('range','range'),
            ('week_day','Week day'),
            ('isnull','Is null'),
            ('regex','Regular Expression'),
            ('iregex','Reg. Exp. (case-insensitive)'),
        ),
        blank=True,
        default = 'icontains',
    )
    filter_value = models.CharField(max_length=2000)
    filter_value2 = models.CharField(max_length=2000, blank=True)
    exclude = models.BooleanField()
    position = models.PositiveSmallIntegerField(blank = True, null = True)
    grouping = models.PositiveSmallIntegerField(default=1)
    #used to group multiple queries together into an AND group, supports OR query logic
    hidden = models.BooleanField(default=False)
    #in order to provide a better UI for end users, some filters present but hidden
    required = models.BooleanField(default=False)
    #allows easy separation of required and non-requied filters - values not 
    #maintained automatically, must be assigned as appropriate


    class Meta:
        ordering = ['grouping', 'position']

    def readable_filter(self):
        read = self.field + " " + self.filter_type + " " + self.filter_value
        if self.filter_value2:
            read += self.filter_value2
        return read
    
    def clean(self):
        if self.filter_type == "range":
            if self.filter_value2 in [None, ""]:
                raise ValidationError('Range filters must have two values')
        return super(FilterField, self).clean()


    def get_choices(self, model, field_name):
        try:
            model_field = model._meta.get_field_by_name(field_name)[0]
        except:
            model_field = None
        if model_field and model_field.choices:
            return model_field.choices

    def process_filter(self):
        """ returns a Q object from a given filter

        """
        filter_field = self
        try:
            # exclude properties from standard ORM filtering 
            if '[property]' in filter_field.field_verbose:
                """
                property_list.append(filter_field)
                return (filter_field, 'property')
                """
                return None
            if '[custom' in filter_field.field_verbose:
                return None

            filter_string = str(filter_field.path + filter_field.field)
            
            if filter_field.filter_type:
                filter_string += '__' + str(filter_field.filter_type)
            
            # Check for special types such as isnull
            if filter_field.filter_type == "isnull" and filter_field.filter_value == "0":
                filter_ = (filter_string, False)
            elif filter_field.filter_type == "in":
                filter_ = (filter_string, str(filter_field.filter_value).split(','))
            else:
                # All filter values are stored as strings, but may need to be converted
                if '[Date' in filter_field.field_verbose:
                    filter_value = parser.parse(filter_field.filter_value)
                    if settings.USE_TZ:
                        filter_value = timezone.make_aware(
                            filter_value,
                            timezone.get_current_timezone()
                        )
                    if filter_field.filter_type == 'range':
                        filter_value = [filter_value, parser.parse(filter_field.filter_value2)]
                        if settings.USE_TZ:
                            filter_value[1] = timezone.make_aware(
                                filter_value[1],
                                timezone.get_current_timezone()
                            )
                else:
                    filter_value = filter_field.filter_value
                    if filter_field.filter_type == 'range':
                        filter_value = [filter_value, filter_field.filter_value2]
                filter_ = (filter_string, filter_value)
            print("filter is", filter_)
            if filter_field.exclude:
                obj = Q(filter_, negate=True)
            else:
                obj = Q(filter_)
            return obj

        except Exception:
            import sys
            e = sys.exc_info()[1]
            message += "Filter Error on %s. If you are using the report builder then " % filter_field.field_verbose
            message += "you found a bug! "
            message += "If you made this in admin, then you probably did something wrong."
            return (None, None)

    @property
    def choices(self):
        if self.pk:
            model = get_model_from_path_string(self.report.root_model.model_class(), self.path)
            return self.get_choices(model, self.field)

    def __unicode__(self):
        return self.field
    
    def __str__(self):
        return self.field + " " + self.filter_type + " " + self.filter_value + " " +self.report.__str__()
   
@python_2_unicode_compatible
class RequiredFilter(models.Model):
    """Establish requirements that a report must contain certain filters in order to be 'valid';
    currently only an existence check - additional fields/constraints can be added later as
    needed"""

    report = models.ForeignKey(Report)
    name = models.CharField(max_length=255)
    field = models.CharField(max_length=2000)
    filterfield = models.ForeignKey("FilterField", blank=True, null=True, default=None)
    or_requires= models.ForeignKey('self', blank=True, null=True, default=None)
    #chain together filters that are required with OR logic - 
    #i.e. This OR That filter required for this report
    whitelist = models.ForeignKey('Whitelist', blank=True, null=True, default=None)

    def check_exist(self):
        return self.report.filterfield_set.filter(field=field).exists()

    def requirements_met(self):
        #assumes default id system - wrong if id=0
        if not self.or_requires:
            return bool(self.filterfield)
        else:
            return (bool(self.filterfield) or self.or_requires.requirements_met())

    def create_filter(self):
        if not self.whitelist:
            raise ValueError()
        return FilterField(
                report=self.report,
                field=self.whitelist.field,
                path=self.whitelist.path,
                path_verbose=self.whitelist.path_verbose,
                field_verbose=self.whitelist.field_verbose,
                required=True,
                )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class GraphField(models.Model):
    """Designates display fields to turn into lists of x, y, and ordered pairs 
    for graphing

    """
    report = models.ForeignKey('Report')
    x_values = models.ForeignKey('DisplayField', related_name="x_values")
    y_values = models.ForeignKey('DisplayField', related_name="y_values")

    def graph_values(self):
        grouping = self.get_grouping()
        listx, listy = (defaultdict(list) for i in range(2))
        query = self.report.get_query()
        print(query)
        x0, y0 = None, None
        for i, value in enumerate(query):
            print("value", value)
            if grouping:
                print('grouping', grouping)
                key = "".join(value.get(x, "") for x in grouping)
            else:
                key = ""
            print("key", key)
            print(self.x_values.field)
            x = self.x_values.format_value(value[self.x_values.get_path_key()])
            y = self.y_values.format_value(value[self.y_values.get_path_key()])
            listx[key+"_x"].append(x) 
            listy[key+"_y"].append(y) 
        print('listx', listx)
        print('listy', listy)
        return (listx, listy)

    def y_list(self):
        pass

    def pairs_list(self):
        pass
    
    def __str__(self):
        return "Graph of " + self.x_values.name + " vs " + self.y_values.name

    def get_grouping(self):
        grouping = [x.path+x.field for x in self.report.displayfield_set.filter(
                group=True).exclude(id=self.x_values.id).exclude(id=self.y_values.id)]
        return grouping

@python_2_unicode_compatible
class Whitelist(models.Model):
    """For a given root model, store path information to allow for creation of
    whitelists of fields for simplified UI/X.  Possible expansion to displayfields?
    """

    #root_model = models.ForeignKey(ContentType, limit_choices_to={'pk__in':_get_allowed_models})
    root_model = models.ForeignKey(ContentType)
    path = models.CharField(max_length=2000, blank=True)
    path_verbose = models.CharField(max_length=2000, blank=True)
    field = models.CharField(max_length=2000)
    field_verbose = models.CharField(max_length=2000)
    
    def __str__(self):
        return self.path_verbose + " "  + self.field_verbose






