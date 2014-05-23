# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CurrentAnnotation'
        db.create_table(u'shared_currentannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Account'])),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.AnnotationKey'])),
            ('value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.AnnotationValue'])),
        ))
        db.send_create_signal(u'shared', ['CurrentAnnotation'])

        # Adding index on 'CurrentAnnotation', fields ['key', 'value']
        db.create_index(u'shared_currentannotation', ['key_id', 'value_id'])

        # Adding model 'AnnotationValue'
        db.create_table(u'shared_annotationvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'shared', ['AnnotationValue'])

        # Adding field 'Annotation.value_ref'
        db.add_column(u'shared_annotation', 'value_ref',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.AnnotationValue'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing index on 'CurrentAnnotation', fields ['key', 'value']
        db.delete_index(u'shared_currentannotation', ['key_id', 'value_id'])

        # Deleting model 'CurrentAnnotation'
        db.delete_table(u'shared_currentannotation')

        # Deleting model 'AnnotationValue'
        db.delete_table(u'shared_annotationvalue')

        # Deleting field 'Annotation.value_ref'
        db.delete_column(u'shared_annotation', 'value_ref_id')


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
            'hidden_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hidden_by': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationKey']"}),
            'value': ('django.db.models.fields.TextField', [], {}),
            'value_ref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationValue']", 'null': 'True'})
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
        },
        u'shared.annotationtemplate': {
            'Meta': {'object_name': 'AnnotationTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        },
        u'shared.annotationtemplateentry': {
            'Meta': {'object_name': 'AnnotationTemplateEntry'},
            'annotation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationKey']"}),
            'choices': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'default': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'field_max_length': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'field_min_length': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'field_required': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'field_size': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationTemplate']"}),
            'type': ('django.db.models.fields.TextField', [], {'default': "'field'"})
        },
        u'shared.annotationvalue': {
            'Meta': {'object_name': 'AnnotationValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        },
        u'shared.client': {
            'Meta': {'object_name': 'Client'},
            'auth_token': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        },
        u'shared.currentannotation': {
            'Meta': {'object_name': 'CurrentAnnotation', 'index_together': "[['key', 'value']]"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationKey']"}),
            'value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationValue']"})
        }
    }

    complete_apps = ['shared']