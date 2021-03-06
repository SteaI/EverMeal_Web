﻿# coding: utf-8
# -*-coding:utf-8

import datetime

import requests
import json
import re

from app.model.neis import MealCache, Neis
from app.database import DBManager

allergy = [u'①', u'②', u'③', u'④', u'⑤', u'⑥', u'⑦', u'⑧', u'⑨', u'⑩', u'⑪', u'⑫', u'⑬', u'⑭', u'⑮', u'⑯', u'⑰', u'⑱']

url_meal = "http://stu.%s.kr/sts_sci_md00_001.do"

w_break = u"조식"
w_lunch = u"중식"
w_dinner = u"석식"

meal_dataPattern = "<tbody>([\S\s\W\w]*)<\/tbody>"
meal_pattern = "<div>(\d+)(.*)<\/div"
meal_semiDataPattern = u"\[(조식|중식|석식)\]([^\[]*)"
meal_dayPattern = "<td><div>(\d+)<br ?\/>"

meal_allergyPattern = "(%s)" % '|'.join(allergy)


preset = {
    'sen.go': u'서울특별시',
    'pen.go': u'부산광역시',
    'dge.go': u'대구광역시',
    'ice.go': u'인천광역시',
    'gen.go': u'광주광역시',
    'dje.go': u'대전광역시',
    'use.go': u'울산광역시',
    'sje.go': u'세종특별자치시',
    'goe.go': u'경기도',
    'kwe.go': u'강원도',
    'cbe.go': u'충청북도',
    'cne.go': u'충청남도',
    'jbe.go': u'전라북도',
    'jne.go': u'전라남도',
    'gbe': u'경상북도',
    'gne.go': u'경상남도',
    'jje.go': u'제주특별자치도',
}


class EducationOffice:
    UnKnown = ""
    Seoul = "sen.go"
    Busan = "pen.go"
    Daegue = "dge.go"
    Incheon = "ice.go"
    Gwanju = "gen.go"
    Daejeon = "dje.go"
    Ulsan = "use.go"
    Saezong = "sje.go"
    Gyunggi = "goe.go"
    Gangwon = "kwe.go"
    ChungchungBookdo = "cbe.go"
    ChungchungNamdo = "cne.go"
    JeonraBookdo = "jbe.go"
    JeonraNamdo = "jne.go"
    GyunasangBookdo = "gbe"
    GyunasangNamdo = "gne.go"
    Jaeju = "jje.go"

    @staticmethod
    def toString(self):
        return preset[str(self)]

class MealType:
    Unknown = 0
    Breakfast = 1
    Lunch = 2
    Dinner = 3

class Allergy:
    Unknown = 0
    turbulence = 1
    milk = 2
    buckwheat = 3
    peanut = 4
    Soy = 5
    wheat = 6
    mackerel = 7
    crap = 8
    shrimp = 9
    pork = 10
    peach = 11
    tomato = 12
    sulfurousAcids = 13
    walnut = 14
    chicken = 15
    beif = 16
    squid = 17
    shellfish = 18

    @staticmethod
    def fromString(find):
        find = unicode(find)
        idx = index(allergy, lambda item: item == find)

        if idx is not None:
            return idx + 1
        else:
            return 0


class DishData:
    def __init__(self):
        self.Name = ""
        self.Types = []

    def toDict(self):
        return \
            {
                "name": self.Name,
                "types": [t for t in self.Types]
            }

    def __str__(self):
        return str(self.toDict())


class Meal:
    def __init__(self):
        self.Type = MealType.Unknown
        self.Dishes = []

    def toDict(self):
        return \
            {
                "type": int(self.Type),
                "dishes": [d.toDict() for d in self.Dishes]
            }

    def __str__(self):
        return str(self.toDict())


class MealData:
    def __init__(self):
        self.Date = str(datetime.date.today())
        self.Breakfast = Meal()
        self.Lunch = Meal()
        self.Dinner = Meal()

    def toDict(self):
        return \
            {
                "date": self.Date,
                "breakfast": self.Breakfast.toDict(),
                "lunch": self.Lunch.toDict(),
                "dinner": self.Dinner.toDict()
            }

    def __str__(self):
        return str(self.toDict())


class SchoolData:
    def __init__(self):
        self.Name = ""
        self.ZipAddress = ""
        self.Code = ""
        self.EducationOffice = EducationOffice.UnKnown
        self.EducationCode = ""
        self.KindScCode = ""
        self.CrseScCode = ""

    def __str__(self):
        return \
            {
                "name": self.name,
                "zipAddress": self.ZipAddress,
                "code": self.Code,
                "educationOffice": self.EducationOffice,
                "educationCode": self.EducationCode,
                "kindScCode": self.KindScCode,
                "crseScCode": self.CrseScCode
            }

class NeisEngine:
    @staticmethod
    def Search(schoolName, edu):
        url = 'http://par.' + str(edu) + '.kr/spr_ccm_cm01_100.do'
        print(url)
        params = \
            {
                'kraOrgNm': schoolName,
                'atptOfcdcScCode': "",
                'srCode': ""
            }

        data = json.loads(requests.get(url, params=params).text)

        for d in data['resultSVO']['orgDVOList']:
            sd = SchoolData()
            sd.EducationOffice = edu
            sd.Name = d['kraOrgNm']
            sd.Code = d['orgCode']
            sd.ZipAddress = d['zipAdres']
            sd.EducationCode = d['atptOfcdcOrgCode']
            sd.KindScCode = d['schulKndScCode']
            sd.CrseScCode = d['schulCrseScCode']
            yield sd

    @staticmethod
    def GetMeals(self, year, month):
        url = url_meal % str(self.EducationOffice)
        print(url)
        postData = \
            {
                "insttNm": self.Name,
                "schulCode": self.Code,
                "schulCrseScCode": self.CrseScCode,
                "schulKndScCode": self.KindScCode,
                "ay": year,
                "mm": "%02d" % int(month)
            }

        html = requests.post(url, data=postData).text
        h_match = re.match(meal_dataPattern, html)

        if h_match:
            html = h_match.group(1)

        idx = 0
        days = re.findall(meal_dayPattern, html)

        for m in re.findall(meal_pattern, html):
            if len(m[1]) > 0:
                day = days[idx]
                idx += 1

                if idx >= len(days):
                    idx -= 1

                meal = MealData()
                meal.Date = str(year) + "-" + str(month) + "-" + day

                for sm in re.findall(meal_semiDataPattern, m[1]):
                    dishes = []

                    for d in re.split("<br ?\/>", sm[1].strip('<br \/>')):
                        dd = DishData()
                        dd.Name = re.sub(meal_allergyPattern, "", d)
                        dd.Types = [Allergy.fromString(x) for x in re.findall(meal_allergyPattern, d)]
                        dishes.append(dd)

                    if sm[0] == w_break:
                        meal.Breakfast.Type = MealType.Lunch
                        meal.Breakfast.Dishes = dishes
                    elif sm[0] == w_lunch:
                        meal.Lunch.Type = MealType.Lunch
                        meal.Lunch.Dishes = dishes
                    elif sm[0] == w_dinner:
                        meal.Dinner.Type = MealType.Lunch
                        meal.Dinner.Dishes = dishes

                yield meal

    @staticmethod
    def SearchFromName(schoolName):
        for s in Neis.query.filter(Neis.name.like("%" + schoolName + "%")).all():
            yield NeisEngine.toSchoolStruct(s)


    @staticmethod
    def SearchFromToken(token):
        for s in Neis.query.filter(Neis.token == token).all():
            yield NeisEngine.toSchoolStruct(s)


    @staticmethod
    def toSchoolStruct(neis):
        school = SchoolData()
        school.EducationOffice = neis.education_office
        school.Name = neis.name
        school.Code = neis.code
        school.KindScCode = neis.kind_sc_code
        school.CrseScCode = neis.crse_sc_Code
        school.ZipAddress = neis.zip_address

        return school


    @staticmethod
    def GetJsonMeals(self, year, month):
        jData = ""
        d = str(year) + "_" + str(month)
        mData = MealCache.query.filter_by(code=self.Code, update_date=d).first()

        if mData is None:
            jData = json.dumps([m.toDict() for m in NeisEngine.GetMeals(self, year, month)])

            DBManager.db.session.add(MealCache(self.Code, jData, d))
            DBManager.db.session.commit()
        else:
            jData = mData.json

        return jData



def index(l, f):
    return next((i for i in range(len(l)) if f(l[i])), None)
