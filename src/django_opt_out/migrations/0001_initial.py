# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-08 13:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_powerbank.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OptOut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('ts', models.DateTimeField(auto_now=True, verbose_name='update timestamp')),
                ('confirmed', models.DateTimeField(blank=True, null=True, verbose_name='confirmation timestamp')),
                ('data', django_powerbank.db.models.fields.JSONField(blank=True, default='{}', null=True, verbose_name='extra data')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('secret', django_powerbank.db.models.fields.SecretField(max_length=200)),
                ('ssl', models.NullBooleanField()),
                ('host', models.CharField(blank=True, max_length=200, null=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('ua', models.CharField(blank=True, max_length=200, null=True)),
                ('cookies', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'out out',
                'verbose_name_plural': 'out outs',
                'default_related_name': 'out_outs',
            },
        ),
        migrations.CreateModel(
            name='OptOutFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=250, verbose_name='question')),
                ('default', models.BooleanField(default=False, verbose_name='checked by default')),
            ],
            options={
                'verbose_name': 'feedback question',
                'verbose_name_plural': 'feedback questions',
                'default_related_name': 'feedback',
            },
        ),
        migrations.CreateModel(
            name='OptOutTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='tag name')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'default_related_name': 'tag_names',
            },
        ),
        migrations.CreateModel(
            name='OptOutTagValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, db_index=True, max_length=80, null=True, verbose_name='tag value')),
                ('opt_out', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='django_opt_out.OptOut')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tags', to='django_opt_out.OptOutTag')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'default_related_name': 'tags',
            },
        ),
        migrations.AddField(
            model_name='optoutfeedback',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='feedback', to='django_opt_out.OptOutTag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='optout',
            name='feedback',
            field=models.ManyToManyField(related_name='out_outs', to='django_opt_out.OptOutFeedback', verbose_name='feedback'),
        ),
    ]
