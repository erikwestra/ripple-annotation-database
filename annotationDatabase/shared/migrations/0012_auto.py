# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AnnotationTemplateEntry.is_public'
        db.add_column(u'shared_annotationtemplateentry', 'is_public',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AnnotationTemplateEntry.is_public'
        db.delete_column(u'shared_annotationtemplateentry', 'is_public')


    models = {
        u'shared.account': {
            'Meta': {'object_name': 'Account'},
            'address': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.User']", 'null': 'True'})
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
            'value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationValue']", 'null': 'True'})
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
            'is_public': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
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
            'Meta': {'unique_together': "[['account', 'key']]", 'object_name': 'CurrentAnnotation', 'index_together': "[['key', 'value']]"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Account']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationKey']"}),
            'value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.AnnotationValue']"})
        },
        u'shared.session': {
            'Meta': {'object_name': 'Session'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_access': ('django.db.models.fields.DateTimeField', [], {}),
            'session_token': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.User']"})
        },
        u'shared.user': {
            'Meta': {'object_name': 'User'},
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_hash': ('django.db.models.fields.TextField', [], {}),
            'password_salt': ('django.db.models.fields.TextField', [], {}),
            'username': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['shared']