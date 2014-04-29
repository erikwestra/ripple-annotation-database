# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'authentication_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('pass_salt', self.gf('django.db.models.fields.TextField')()),
            ('pass_hash', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'authentication', ['User'])

        # Adding model 'Session'
        db.create_table(u'authentication_session', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_token', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authentication.User'])),
            ('last_access', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'authentication', ['Session'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'authentication_user')

        # Deleting model 'Session'
        db.delete_table(u'authentication_session')


    models = {
        u'authentication.session': {
            'Meta': {'object_name': 'Session'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_access': ('django.db.models.fields.DateTimeField', [], {}),
            'session_token': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authentication.User']"})
        },
        u'authentication.user': {
            'Meta': {'object_name': 'User'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pass_hash': ('django.db.models.fields.TextField', [], {}),
            'pass_salt': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.TextField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['authentication']