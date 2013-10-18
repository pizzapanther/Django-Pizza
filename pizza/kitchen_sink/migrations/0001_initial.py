# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Blurb'
        db.create_table(u'kitchen_sink_blurb', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('etype', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'kitchen_sink', ['Blurb'])

        # Adding model 'File'
        db.create_table(u'kitchen_sink_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'kitchen_sink', ['File'])

        # Adding model 'Image'
        db.create_table(u'kitchen_sink_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('caption_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('credit_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'kitchen_sink', ['Image'])

        # Adding model 'ImageSet'
        db.create_table(u'kitchen_sink_imageset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('captype', self.gf('django.db.models.fields.CharField')(default='override', max_length=10)),
        ))
        db.send_create_signal(u'kitchen_sink', ['ImageSet'])

        # Adding model 'ImageSetItem'
        db.create_table(u'kitchen_sink_imagesetitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Image'])),
            ('imageset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.ImageSet'])),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('caption_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('credit_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('sorder', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'kitchen_sink', ['ImageSetItem'])

        # Adding model 'Author'
        db.create_table(u'kitchen_sink_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Image'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'kitchen_sink', ['Author'])

        # Adding M2M table for field sites on 'Author'
        m2m_table_name = db.shorten_name(u'kitchen_sink_author_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('author', models.ForeignKey(orm[u'kitchen_sink.author'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['author_id', 'site_id'])

        # Adding model 'Page'
        db.create_table(u'kitchen_sink_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tpl', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'kitchen_sink', ['Page'])

        # Adding M2M table for field sites on 'Page'
        m2m_table_name = db.shorten_name(u'kitchen_sink_page_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm[u'kitchen_sink.page'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['page_id', 'site_id'])

        # Adding model 'Redirect'
        db.create_table(u'kitchen_sink_redirect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('goto', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'kitchen_sink', ['Redirect'])

        # Adding M2M table for field sites on 'Redirect'
        m2m_table_name = db.shorten_name(u'kitchen_sink_redirect_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('redirect', models.ForeignKey(orm[u'kitchen_sink.redirect'], null=False)),
            ('site', models.ForeignKey(orm[u'sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['redirect_id', 'site_id'])

        # Adding model 'Version'
        db.create_table(u'kitchen_sink_version', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Page'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('publish', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'kitchen_sink', ['Version'])


    def backwards(self, orm):
        # Deleting model 'Blurb'
        db.delete_table(u'kitchen_sink_blurb')

        # Deleting model 'File'
        db.delete_table(u'kitchen_sink_file')

        # Deleting model 'Image'
        db.delete_table(u'kitchen_sink_image')

        # Deleting model 'ImageSet'
        db.delete_table(u'kitchen_sink_imageset')

        # Deleting model 'ImageSetItem'
        db.delete_table(u'kitchen_sink_imagesetitem')

        # Deleting model 'Author'
        db.delete_table(u'kitchen_sink_author')

        # Removing M2M table for field sites on 'Author'
        db.delete_table(db.shorten_name(u'kitchen_sink_author_sites'))

        # Deleting model 'Page'
        db.delete_table(u'kitchen_sink_page')

        # Removing M2M table for field sites on 'Page'
        db.delete_table(db.shorten_name(u'kitchen_sink_page_sites'))

        # Deleting model 'Redirect'
        db.delete_table(u'kitchen_sink_redirect')

        # Removing M2M table for field sites on 'Redirect'
        db.delete_table(db.shorten_name(u'kitchen_sink_redirect_sites'))

        # Deleting model 'Version'
        db.delete_table(u'kitchen_sink_version')


    models = {
        u'kitchen_sink.author': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Author'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kitchen_sink.Image']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'kitchen_sink.blurb': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Blurb'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'etype': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'kitchen_sink.file': {
            'Meta': {'ordering': "('title',)", 'object_name': 'File'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'kitchen_sink.image': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Image'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'caption_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'credit_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'kitchen_sink.imageset': {
            'Meta': {'ordering': "('title',)", 'object_name': 'ImageSet'},
            'captype': ('django.db.models.fields.CharField', [], {'default': "'override'", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'kitchen_sink.imagesetitem': {
            'Meta': {'ordering': "('sorder',)", 'object_name': 'ImageSetItem'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'caption_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'credit_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kitchen_sink.Image']"}),
            'imageset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kitchen_sink.ImageSet']"}),
            'sorder': ('django.db.models.fields.IntegerField', [], {})
        },
        u'kitchen_sink.page': {
            'Meta': {'ordering': "('url',)", 'object_name': 'Page'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'tpl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'kitchen_sink.redirect': {
            'Meta': {'ordering': "('url',)", 'object_name': 'Redirect'},
            'goto': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'kitchen_sink.version': {
            'Meta': {'ordering': "('-publish', 'id')", 'object_name': 'Version'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kitchen_sink.Page']"}),
            'publish': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['kitchen_sink']