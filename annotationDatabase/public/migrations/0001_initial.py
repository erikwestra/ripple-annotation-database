# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'public_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('password_salt', self.gf('django.db.models.fields.TextField')()),
            ('password_hash', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'public', ['User'])

        # Adding model 'Account'
        db.create_table(u'public_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['public.User'])),
        ))
        db.send_create_signal(u'public', ['Account'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'public_user')

        # Deleting model 'Account'
        db.delete_table(u'public_account')


    models = {
        u'public.account': {
            'Meta': {'object_name': 'Account'},
            'address': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['public.User']"})
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