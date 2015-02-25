TITLE = '4tube'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
BASE_URL = 'http://www.4tube.com'

####################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'

####################################################################################################
@handler('/video/4tube', TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(Video), title='All videos'))
	oc.add(DirectoryObject(key=Callback(Category), title='Categories'))
	oc.add(DirectoryObject(key=Callback(ChannelList), title='Channels'))
	oc.add(DirectoryObject(key=Callback(Pornstar), title='Pornstars'))

	return oc

####################################################################################################
@route('/video/4tube/video')
def Video():

	oc = ObjectContainer(title2='All videos')
	nav = HTML.ElementFromURL(BASE_URL).xpath('//ul[contains(@class, "all-videos-nav")]/li')

	for item in nav:

		title = item.xpath('./a/@title')[0]
		url = item.xpath('./a/@href')[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		oc.add(DirectoryObject(
			key = Callback(VideoList, title=title, url=url),
			title = title
		))

	return oc

####################################################################################################
@route('/video/4tube/category')
def Category():

	oc = ObjectContainer(title2='Categories')
	nav = HTML.ElementFromURL(BASE_URL).xpath('//ul[contains(@class, "categories-nav")]/li')

	for item in nav:

		title = item.xpath('./a/@title')[0]
		url = item.xpath('./a/@href')[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		oc.add(DirectoryObject(
			key = Callback(VideoList, title=title, url=url),
			title = title
		))

	return oc

####################################################################################################
@route('/video/4tube/pornstar')
def Pornstar():

	oc = ObjectContainer(title2='Pornstars')
	nav = HTML.ElementFromURL(BASE_URL).xpath('//ul[contains(@class, "order-alpha")]/li')

	for item in nav:

		title = item.xpath('./a/text()')[0].strip()
		url = item.xpath('./a/@href')

		if len(url) < 1:
			continue
		else:
			url = url[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		oc.add(DirectoryObject(
			key = Callback(PornstarList, title=title.lower(), url=url),
			title = title
		))

	return oc

####################################################################################################
@route('/video/4tube/pornstar/{title}', page=int)
def PornstarList(title, url, page=1):

	oc = ObjectContainer(title2='Pornstars %s' % (title.upper()))

	if not 'sort=name' in url:
		if '?' in url:
			url = '%s&sort=name' % (url)
		else:
			url = '%s?sort=name' % (url)

	html = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK)
	nav = html.xpath('//a[@class="thumb-link"]')

	for item in nav:

		name = item.xpath('./@title')[0]
		thumb = item.xpath('.//img[@data-original]/@data-original')[0]
		url = item.xpath('./@href')[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		oc.add(DirectoryObject(
			key = Callback(VideoList, title=name, url=url),
			title = name,
			thumb = thumb
		))

	next_page = html.xpath('//link[@rel="next"]/@href')

	if len(next_page) > 0:

		url = next_page[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		if page%10 != 0:

			oc.extend(PornstarList(title, url, page=page+1))

		else:

			oc.add(NextPageObject(
				key = Callback(PornstarList, title=title, url=url, page=page+1),
				title = L('More...')
			))

	return oc

####################################################################################################
@route('/video/4tube/video/list', page=int)
def VideoList(title, url, page=1):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(url)
	nav = html.xpath('//a[@class="thumb-link"]')

	for item in nav:

		title = item.xpath('./@title')[0]
		thumb = item.xpath('.//img[@data-master]/@data-master')[0]

		url = item.xpath('./@href')[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		if not '//www.4tube.com/videos' in url:
			continue

		oc.add(VideoClipObject(
			title = title,
			thumb = thumb,
			url = url
		))

	next_page = html.xpath('//link[@rel="next"]/@href')

	if len(next_page) > 0:

		url = next_page[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		if page%5 != 0:

			oc.extend(VideoList(title, url, page=page+1))

		else:

			oc.add(NextPageObject(
				key = Callback(VideoList, title=title, url=url, page=page+1),
				title = L('More...')
			))

	return oc

####################################################################################################
@route('/video/4tube/channel/list', page=int)
def ChannelList(url='http://www.4tube.com/channels', page=1):

	oc = ObjectContainer(title2='Channels')

	html = HTML.ElementFromURL(url, cacheTime=CACHE_1WEEK)
	nav = html.xpath('//a[@class="thumb-link"]')

	for item in nav:

		name = item.xpath('./@title')[0]
		thumb = item.xpath('.//img[@data-original]/@data-original')[0]
		url = item.xpath('./@href')[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		oc.add(DirectoryObject(
			key = Callback(VideoList, title=name, url=url),
			title = name,
			thumb = thumb
		))

	next_page = html.xpath('//link[@rel="next"]/@href')

	if len(next_page) > 0:

		url = next_page[0]

		if not url.startswith('http://'):
			url = '%s/%s' % (BASE_URL, url.lstrip('/'))

		if page%10 != 0:

			oc.extend(ChannelList(url, page=page+1))

		else:

			oc.add(NextPageObject(
				key = Callback(ChannelList, url=url, page=page+1),
				title = L('More...')
			))

	return oc
