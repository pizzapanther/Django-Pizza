# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'calendar_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'calendar', ['Category'])

        # Adding model 'Series'
        db.create_table(u'calendar_series', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'calendar', ['Series'])

        # Adding model 'Event'
        db.create_table(u'calendar_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('start_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_dt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('all_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.Image'], null=True, blank=True)),
            ('imageset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kitchen_sink.ImageSet'], null=True, blank=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['calendar.Series'], null=True, blank=True)),
        ))
        db.send_create_signal(u'calendar', ['Event'])

        # Adding M2M table for field categories on 'Event'
        m2m_table_name = db.shorten_name(u'calendar_event_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'calendar.event'], null=False)),
            ('category', models.ForeignKey(orm[u'calendar.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'category_id'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'calendar_category')

        # Deleting model 'Series'
        db.delete_table(u'calendar_series')

        # Deleting model 'Event'
        db.delete_table(u'calendar_event')

        # Removing M2M table for field categories on 'Event'
        db.delete_table(db.shorten_name(u'calendar_event_categories'))


    models = {
        u'calendar.category': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'calendar.event': {
            'Meta': {'ordering': "('start_dt', '-all_day', 'end_dt')", 'object_name': 'Event'},
            'all_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['calendar.Category']", 'null': 'True', 'blank': 'True'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kitchen_sink.Image']", 'null': 'True', 'blank': 'True'}),
            'imageset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['kitchen_sink.ImageSet']", 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['calendar.Series']", 'null': 'True', 'blank': 'True'}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'calendar.series': {
            'Meta': {'object_name': 'Series'},
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
        }
    }

    complete_apps = ['calendar']