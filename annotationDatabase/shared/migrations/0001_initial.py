# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AnnotationKey'
        db.create_table(u'shared_annotationkey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'shared', ['AnnotationKey'])

        # Adding model 'Account'
        db.create_table(u'shared_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'shared', ['Account'])

        # Adding model 'AnnotationBatch'
        db.create_table(u'shared_annotationbatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_id', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'shared', ['AnnotationBatch'])

        # Adding model 'Annotation'
        db.create_table(u'shared_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.AnnotationBatch'])),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Account'])),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.AnnotationKey'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hidden_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('hidden_by', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'shared', ['Annotation'])


    def backwards(self, orm):
        # Deleting model 'AnnotationKey'
        db.delete_table(u'shared_annotationkey')

        # Deleting model 'Account'
        db.delete_table(u'shared_account')

        # Deleting model 'AnnotationBatch'
        db.delete_table(u'shared_annotationbatch')

        # Deleting model 'Annotation'
        db.delete_table(u'shared_annotation')


    models = {
        u'shared.account': {
            'Meta': {'object_name': 'Account'},
            'address': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'shared.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Account']"}),
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationBatch']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hidden_at': ('django.db.models.fields.DateTimeField', [], {}),
            'hidden_by': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationKey']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'shared.annotationbatch': {
            'Meta': {'object_name': 'AnnotationBatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user_id': ('django.db.models.fields.TextField', [], {})
        },
        u'shared.annotationkey': {
            'Meta': {'object_name': 'AnnotationKey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['shared']