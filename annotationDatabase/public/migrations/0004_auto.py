# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Account'
        db.delete_table(u'public_account')

        # Deleting model 'Session'
        db.delete_table(u'public_session')

        # Deleting model 'User'
        db.delete_table(u'public_user')


    def backwards(self, orm):
        # Adding model 'Account'
        db.create_table(u'public_account', (
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['public.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'public', ['Account'])

        # Adding model 'Session'
        db.create_table(u'public_session', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['public.User'])),
            ('last_access', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_token', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'public', ['Session'])

        # Adding model 'User'
        db.create_table(u'public_user', (
            ('username', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('password_salt', self.gf('django.db.models.fields.TextField')()),
            ('blocked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password_hash', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'public', ['User'])


    models = {
        
    }

    complete_apps = ['public']