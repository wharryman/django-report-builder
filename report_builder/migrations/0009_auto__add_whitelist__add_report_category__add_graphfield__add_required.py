# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Whitelist'
        db.create_table(u'report_builder_whitelist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('root_model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('path_verbose', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('field_verbose', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal(u'report_builder', ['Whitelist'])

        # Adding model 'Report_Category'
        db.create_table(u'report_builder_report_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('about', self.gf('django.db.models.fields.CharField')(default='', max_length=300, blank=True)),
            ('parent_cat', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['report_builder.Report_Category'], null=True, blank=True)),
        ))
        db.send_create_signal(u'report_builder', ['Report_Category'])

        # Adding model 'GraphField'
        db.create_table(u'report_builder_graphfield', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report_builder.Report'])),
            ('x_values', self.gf('django.db.models.fields.related.ForeignKey')(related_name='x_values', to=orm['report_builder.DisplayField'])),
            ('y_values', self.gf('django.db.models.fields.related.ForeignKey')(related_name='y_values', to=orm['report_builder.DisplayField'])),
        ))
        db.send_create_signal(u'report_builder', ['GraphField'])

        # Adding model 'RequiredFilter'
        db.create_table(u'report_builder_requiredfilter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report_builder.Report'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('filterfield', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['report_builder.FilterField'], null=True, blank=True)),
            ('or_requires', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['report_builder.RequiredFilter'], null=True, blank=True)),
            ('whitelist', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['report_builder.Whitelist'], null=True, blank=True)),
        ))
        db.send_create_signal(u'report_builder', ['RequiredFilter'])

        # Adding field 'FilterField.grouping'
        db.add_column(u'report_builder_filterfield', 'grouping',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1),
                      keep_default=False)

        # Adding field 'FilterField.hidden'
        db.add_column(u'report_builder_filterfield', 'hidden',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'FilterField.required'
        db.add_column(u'report_builder_filterfield', 'required',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Report.category'
        db.add_column(u'report_builder_report', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['report_builder.Report_Category'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Report.read_only'
        db.add_column(u'report_builder_report', 'read_only',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'DisplayField.display_format'
        db.alter_column(u'report_builder_displayfield', 'display_format_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['report_builder.Format'], null=True))

    def backwards(self, orm):
        # Deleting model 'Whitelist'
        db.delete_table(u'report_builder_whitelist')

        # Deleting model 'Report_Category'
        db.delete_table(u'report_builder_report_category')

        # Deleting model 'GraphField'
        db.delete_table(u'report_builder_graphfield')

        # Deleting model 'RequiredFilter'
        db.delete_table(u'report_builder_requiredfilter')

        # Deleting field 'FilterField.grouping'
        db.delete_column(u'report_builder_filterfield', 'grouping')

        # Deleting field 'FilterField.hidden'
        db.delete_column(u'report_builder_filterfield', 'hidden')

        # Deleting field 'FilterField.required'
        db.delete_column(u'report_builder_filterfield', 'required')

        # Deleting field 'Report.category'
        db.delete_column(u'report_builder_report', 'category_id')

        # Deleting field 'Report.read_only'
        db.delete_column(u'report_builder_report', 'read_only')


        # Changing field 'DisplayField.display_format'
        db.alter_column(u'report_builder_displayfield', 'display_format_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['report_builder.Format'], unique=True, null=True))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'report_builder.displayfield': {
            'Meta': {'ordering': "['position']", 'object_name': 'DisplayField'},
            'aggregate': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'display_format': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['report_builder.Format']", 'null': 'True', 'blank': 'True'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'field_verbose': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'path_verbose': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['report_builder.Report']"}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sort_reverse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'total': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '15'})
        },
        u'report_builder.filterfield': {
            'Meta': {'ordering': "['grouping', 'position']", 'object_name': 'FilterField'},
            'exclude': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'field_verbose': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'filter_type': ('django.db.models.fields.CharField', [], {'default': "'icontains'", 'max_length': '20', 'blank': 'True'}),
            'filter_value': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'filter_value2': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'grouping': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'path_verbose': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['report_builder.Report']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'report_builder.format': {
            'Meta': {'object_name': 'Format'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'string': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'})
        },
        u'report_builder.graphfield': {
            'Meta': {'object_name': 'GraphField'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['report_builder.Report']"}),
            'x_values': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'x_values'", 'to': u"orm['report_builder.DisplayField']"}),
            'y_values': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'y_values'", 'to': u"orm['report_builder.DisplayField']"})
        },
        u'report_builder.report': {
            'Meta': {'object_name': 'Report'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['report_builder.Report_Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'distinct': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'read_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'root_model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'starred': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'report_starred_set'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'user_created': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'user_modified': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'report_modified_set'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'report_builder.report_category': {
            'Meta': {'object_name': 'Report_Category'},
            'about': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'parent_cat': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['report_builder.Report_Category']", 'null': 'True', 'blank': 'True'})
        },
        u'report_builder.requiredfilter': {
            'Meta': {'object_name': 'RequiredFilter'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'filterfield': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['report_builder.FilterField']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'or_requires': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['report_builder.RequiredFilter']", 'null': 'True', 'blank': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['report_builder.Report']"}),
            'whitelist': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['report_builder.Whitelist']", 'null': 'True', 'blank': 'True'})
        },
        u'report_builder.whitelist': {
            'Meta': {'object_name': 'Whitelist'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'field_verbose': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'path_verbose': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'root_model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"})
        }
    }

    complete_apps = ['report_builder']
