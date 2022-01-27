# test code for paste 
'''
for web from these two sites:
'https://justpaste.it',
'https://pastebin.com',
'''
import paste


urls = ''' 
(list) input your test url here 
'''

for url in urls:
    try:
        page_info = paste.main(url)
        assert len(page_info['posts']) > 0
        assert page_info['views'] >= 0
    except Exception as e:
        print(url)
        print(e)