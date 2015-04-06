#
#  All of the Season related concepts to be stored in the cache
#

from datetime import datetime
from datetime import date
from datetime import timedelta

import sys

SEASON_CHOICES = (
    (1, 'Winter'),
    (2, 'Spring'),
    (3, 'Summer'),
    (4, 'Fall'),
)

# class Season(models.Model):
#     season = models.IntegerField(choices=SEASON_CHOICES)
#     year = models.IntegerField()
    
#     start_date = models.DateField('season start date')
#     end_date = models.DateField('season end date')
    
#     def __str__(self):
#         return str(

class Season():
    season = ""
    year = 2015
    start_date = None
    end_date = None
    sort_key = 20151
    
    def __str__(self):
        return self.season + ' ' + str(self.year)

class SeasonCache():
    # Keys are like: Winter2015
    
    seasons = {}
    
    def get(self, the_date):
        key = self.get_key(the_date)
        
        if key and key in self.seasons.keys():
            return self.seasons.get(key)
            
        return None
        
    def __get_season_name(self, the_date):
        month = the_date.month
        season = None        

        if month <= 3:
            season = "Winter"
        elif month <= 6:
            season = "Spring"
        elif month <= 9:
            season = "Summer"
        else:
            season = "Fall" 
            
        return season
        
    def get_key(self, the_date):
        year = the_date.year
        season = self.__get_season_name(the_date)

        if season:
            return season + str(year)
    
        return None
    
    # Adds, if not already present
    def add(self, the_date):
        key = self.get_key(the_date)
        
        if key in self.seasons.keys():
            return
        
        # Otherwise, add it
        year = the_date.year
        month = the_date.month
        
        s = Season()

        s.year = year
        if month <= 3:
            s.season = "Winter"
            s.start_date = date(year, 1, 1)
            s.end_date = date(year, 4, 1) + timedelta(days=-1)
            s.sort_key = year * 10 + 1
        elif month <= 6:
            s.season = "Spring"
            s.start_date = date(year, 4, 1)
            s.end_date = date(year, 7, 1) + timedelta(days=-1)
            s.sort_key = year * 10 + 2
        elif month <= 9:
            s.season = "Summer"
            s.start_date = date(year, 7, 1)
            s.end_date = date(year, 10, 1) + timedelta(days=-1)
            s.sort_key = year * 10 + 3
        else:
            s.season = "Fall"
            s.start_date = date(year, 10, 1)
            s.end_date = date(year + 1, 1, 1) + timedelta(days=-1)
            s.sort_key = year * 10 + 4

        self.seasons[key] = s         
        return s
        
    def all(self):
        return sorted(self.seasons.values(), key=lambda x: x.sort_key)
