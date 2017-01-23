#
#  All of the Season related concepts to be stored in the cache
#

from datetime import datetime
from datetime import date
from datetime import timedelta

import sys

# SEASON_CHOICES = (
#     (1, 'Winter'),
#     (2, 'Spring'),
#     (3, 'Summer'),
#     (4, 'Fall'),
# )

# class Season(models.Model):
#     season = models.IntegerField(choices=SEASON_CHOICES)
#     year = models.IntegerField()
    
#     start_date = models.DateField('season start date')
#     end_date = models.DateField('season end date')
    
#     def __str__(self):
#         return str(
#
# class Season():
#     season = ""
#     year = 2015
#     start_date = None
#     end_date = None
#     sort_key = 20151
#
#     def __str__(self):
#         return self.season + ' ' + str(self.year)