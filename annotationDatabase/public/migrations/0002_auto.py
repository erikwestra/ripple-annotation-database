# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Session'
        db.create_table(u'public_session', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_token', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['public.User'])),
            ('last_access', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'public', ['Session'])


    def backwards(self, orm):
        # Deleting model 'Session'
        db.delete_table(u'public_session')


    models = {
        u'public.account': {
            'Meta': {'object_name': 'Account'},
            'address': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['public.User']"})
        },
        u'public.session': {
            'Meta': {'object_name': 'Session'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_access': ('django.db.models.fields.DateTimeField', [], {}),
            'session_token': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['public.User']"})
        },
        u'public.user': {
            'Meta': {'object_name': 'User'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_hash': ('django.db.models.fields.TextField', [], {}),
            'password_salt': ('django.db.models.fields.TextField', [], {}),
            'username': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        }
    }

    complete_apps = ['public']