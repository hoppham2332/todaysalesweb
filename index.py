from whoosh.index import create_in
from whoosh.fields import TEXT,KEYWORD,ID,Schema
import os.path
import json
import sys
import datetime
import boto3
from path import Path
"""File name is deals_ + datetime with YearMonthDay"""
daystr = datetime.date.today().strftime('%Y%m%d')
filename = 'deals_'+daystr+'.jl'
rootFolder = 'C:\crawlData\\'
"""Remove last raw data file """
oldFiles = Path(rootFolder).files('*.jl')
oldFiles[0].remove()
print('Removed {} file').format(oldFiles[0])
fullFilePath = rootFolder+filename
"""Download deals from S3"""
session = boto3.Session(profile_name='indexingProf')
s3_client = session.client('s3')
s3_client.download_file('home-deals', 'deals/'+filename, fullFilePath)


# ixDirectory = 'indexed_'+daystr
ixDirectory = rootFolder + 'indexed'
dealSchema = Schema(title=TEXT(stored=True),img=ID(stored=True),link=TEXT(stored=True),price=ID(stored=True))
if not os.path.exists(ixDirectory):
    os.mkdir(ixDirectory)
ix = create_in(ixDirectory,dealSchema)
writer = ix.writer()

"""Configuration for indexing full-text search by whoosh"""
with open(fullFilePath) as file:			
	for line in file:			
		try:
			lineData = json.loads(line)
			title = lineData['title']
			img = lineData['img']
			link = lineData['link']
			price = lineData['prices']['pSale']
			writer.add_document(title=title, img=img, link=link, price=price)
		except ValueError as e:
			continue	
	writer.commit()
	print('Indexing file '+filename + ' to the ' + ixDirectory +' completed.')
