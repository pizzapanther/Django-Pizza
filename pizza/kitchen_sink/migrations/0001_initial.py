# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table('kitchen_sink_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('kitchen_sink', ['File'])

        # Adding model 'Image'
        db.create_table('kitchen_sink_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('kitchen_sink', ['Image'])

        # Adding model 'Template'
        db.create_table('kitchen_sink_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('kitchen_sink', ['Template'])

        # Adding model 'TemplateRegion'
        db.create_table('kitchen_sink_templateregion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Template'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('cvar', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('etype', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('kitchen_sink', ['TemplateRegion'])

        # Adding model 'Page'
        db.create_table('kitchen_sink_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Template'])),
        ))
        db.send_create_signal('kitchen_sink', ['Page'])

        # Adding M2M table for field sites on 'Page'
        db.create_table('kitchen_sink_page_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm['kitchen_sink.page'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('kitchen_sink_page_sites', ['page_id', 'site_id'])

        # Adding model 'Redirect'
        db.create_table('kitchen_sink_redirect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('goto', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('kitchen_sink', ['Redirect'])

        # Adding M2M table for field sites on 'Redirect'
        db.create_table('kitchen_sink_redirect_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('redirect', models.ForeignKey(orm['kitchen_sink.redirect'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('kitchen_sink_redirect_sites', ['redirect_id', 'site_id'])

        # Adding model 'Version'
        db.create_table('kitchen_sink_version', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Page'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('publish', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('kitchen_sink', ['Version'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table('kitchen_sink_file')

        # Deleting model 'Image'
        db.delete_table('kitchen_sink_image')

        # Deleting model 'Template'
        db.delete_table('kitchen_sink_template')

        # Deleting model 'TemplateRegion'
        db.delete_table('kitchen_sink_templateregion')

        # Deleting model 'Page'
        db.delete_table('kitchen_sink_page')

        # Removing M2M table for field sites on 'Page'
        db.delete_table('kitchen_sink_page_sites')

        # Deleting model 'Redirect'
        db.delete_table('kitchen_sink_redirect')

        # Removing M2M table for field sites on 'Redirect'
        db.delete_table('kitchen_sink_redirect_sites')

        # Deleting model 'Version'
        db.delete_table('kitchen_sink_version')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'kitchen_sink.file': {
            'Meta': {'ordering': "('title',)", 'object_name': 'File'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'kitchen_sink.image': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Image'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'kitchen_sink.page': {
            'Meta': {'ordering': "('url',)", 'object_name': 'Page'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kitchen_sink.Template']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'kitchen_sink.redirect': {
            'Meta': {'ordering': "('url',)", 'object_name': 'Redirect'},
            'goto': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'kitchen_sink.template': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Template'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'kitchen_sink.templateregion': {
            'Meta': {'ordering': "('order',)", 'object_name': 'TemplateRegion'},
            'cvar': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'etype': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kitchen_sink.Template']"})
        },
        'kitchen_sink.version': {
            'Meta': {'ordering': "('-publish', 'id')", 'object_name': 'Version'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kitchen_sink.Page']"}),
            'publish': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['kitchen_sink']