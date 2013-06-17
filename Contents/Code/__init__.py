TITLE = '4tube'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
BASE_URL = 'http://www.4tube.com'

ALL_VIDEOS_URL = '%s/videos/data?subListAction=&sort=%%s&page=%%%%d' % BASE_URL
PORNSTARS_AZ_URL = '%s/pornstars/%%s?sort=%%s&page=%%%%d' % BASE_URL
PORNSTAR_URL = '%s/pornstars/%%s?sort=%%s&page=%%%%d' % BASE_URL
TAGS_URL = '%s/find/tags/%%s?data=1&sort=%%s&page=%%%%d' % BASE_URL

RE_DURATION = Regex('(\d+)min (\d+)sec')

####################################################################################################
def Start():

	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	NextPageObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0'

####################################################################################################
@handler('/video/4tube', TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer(view_group='List')

	oc.add(DirectoryObject(key=Callback(BrowseAllVideos, title='Browse All Videos'), title='Browse All Videos'))
	oc.add(DirectoryObject(key=Callback(PornstarsAZ, title='Pornstars A-Z'), title='Pornstars A-Z'))
	oc.add(DirectoryObject(key=Callback(MostPopularTags, title='Most Popular Tags'), title='Most Popular Tags'))
	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))

	return oc

####################################################################################################
@route('/video/4tube/videos/all')
def BrowseAllVideos(title):

	url = ALL_VIDEOS_URL % Prefs['sort_video']
	return GetVideos(url, title=title)

####################################################################################################
@route('/video/4tube/pornstars/alphabetically')
def PornstarsAZ(title):

	oc = ObjectContainer(title2=title, view_group='List')

	for char in list(String.UPPERCASE):
		oc.add(DirectoryObject(
			key = Callback(Pornstars, char=char),
			title = char
		))

	return oc

####################################################################################################
@route('/video/4tube/pornstars/{char}')
def Pornstars(char):

	oc = ObjectContainer(title2=char, view_group='List')
	url = PORNSTARS_AZ_URL % (char, Prefs['sort_pornstar'])

	# Get the number of pages
	pages = HTML.ElementFromURL(url % 1, cacheTime=CACHE_1WEEK).xpath('//span[@class="pagination"]')

	if len(pages) < 1:
		pages = 1
	else:
		pages = pages[0].xpath('./a[last()]')[0].get('href')
		pages = int(pages.split('page=')[-1])

	# Loop over all the pages to grab all pornstar names and info
	for i in range (1, pages+1):
		pornstars = HTML.ElementFromURL(url % i, cacheTime=CACHE_1WEEK).xpath('//div[@class="pornstarInfo_large"]')

		for p in pornstars:
			name = p.xpath('./span[contains(@class, "pornstar")]/a/text()')[0].strip()
			thumb = p.xpath('./a/img/@src')[0].replace('/161x161.jpeg', '/300x300.jpeg')

			oc.add(DirectoryObject(
				key = Callback(Pornstar, name=name, url_name=name.lower().replace(' ', '-')),
				title = name,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
			))

	return oc

####################################################################################################
@route('/video/4tube/pornstar/{url_name}/videos')
def Pornstar(name, url_name):

	url = PORNSTAR_URL % (url_name, Prefs['sort_video'])
	return GetVideos(url, title=name)

####################################################################################################
@route('/video/4tube/tags')
def MostPopularTags(title):

	oc = ObjectContainer(title2=title, view_group='List')
	tags = HTML.ElementFromURL(BASE_URL).xpath('//div[@class="tags"]//a[text()!=""]')

	for t in tags:
		title = t.text.strip().title()
		tag = t.get('href').split('/')[-1]

		oc.add(DirectoryObject(
			key = Callback(Tag, title=title, tag=tag),
			title = title
		))

	return oc

####################################################################################################
@route('/video/4tube/tag/{tag}')
def Tag(title, tag):

	url = TAGS_URL % (tag, Prefs['sort_video'])
	return GetVideos(url, title=title)

####################################################################################################
@route('/video/4tube/videos', page=int)
def GetVideos(url, title, page=1):

	oc = ObjectContainer(title2=title, view_group='InfoList')
	html = HTML.ElementFromURL(url % page)
	videos = html.xpath('//div[@class="videoInfo"]')

	for v in videos:
		name = v.xpath('./span[contains(@class, "pornstar")]/a/strong/text()')[0].strip()
		video_url = v.xpath('./a/@href')[0]
		thumb = v.xpath('./a/img/@src')[0].replace('/160x120/', '/320x240/')
		summary = v.xpath('./a/img[@class="thumb"]/@title')[0].strip()
		duration = v.xpath('./span[@class="info"]/span[@class="length"]/text()')[0]
		duration = TimeToMs(duration)
		rating = v.xpath('./span[@class="info"]/span[@class="rating"]//span[@class="full"]')
		rating = float(len(rating) * 2)

		oc.add(VideoClipObject(
			url = video_url,
			title = name,
			summary = summary,
			duration = duration,
			rating = rating,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
		))

	# Next page
	pages = html.xpath('//span[@class="pagination"]')

	if len(pages) < 1:
		pages = 1
	else:
		pages = pages[0].xpath('./a[last()]')[0].get('href')
		pages = int(pages.split('page=')[-1])

	if page < pages:
		oc.add(NextPageObject(
			key = Callback(GetVideos, title=title, url=url, page=page+1),
			title = L('More...')
		))

	return oc

####################################################################################################
def TimeToMs(timecode):

	seconds = 0
	duration = list(RE_DURATION.findall(timecode)[0])
	duration.reverse()

	for i in range(0, len(duration)):
		seconds += int(duration[i]) * (60**i)

	return seconds * 1000
