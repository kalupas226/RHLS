# -*- coding: utf-8 -*-
import re
import mechanize

name = "小熊 幸一郎　（おぐま こういちろう）　1866年～1952年"
nameReg = r"(?<=[(（]).*?(?=[)）])"
name = re.sub(nameReg, "", name)
name = re.sub(r"\d","",name)
print(name)
