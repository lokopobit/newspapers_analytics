# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 22:01:14 2020

@author: lokopobit
"""

# Load external libreries
import newspaper

# Building a news source
paper = newspaper.build('https://www.diariodehuelva.es/', language='es', memoize_articles=False)

# Extracting articles
for article in paper.articles:
    print(article.url)
    
print(paper.size())

# Extracting source categories
for category in paper.category_urls():
    print(category)

# Extracting source feeds
for feed_url in paper.feed_urls():
    print(feed_url)
    
# Extracting source brand and description
print(paper.brand)
print(paper.description)

## NEWS ARTICLES ##
# Downloading an article
article1 = paper.articles[0]
article1.download()
print(article1.html)

# Parsing an article
article1.parse()
print(article1.text)
print(article1.top_image)
print(article1.authors)
print(article1.title)
print(article1.images)
print(article1.movies)

# Performing NLP on an article
article1.nlp()
print(article1.summary)
print(article1.keywords)


# # # # # # # # # #
# for key in urls_dict.keys():
#     print(key)
#     urls = urls_dict[key]
#     for url in urls:
#         url = url.split('_')
#         print(url[0])
#         paper = newspaper.build(url[1], language='es')
#         print(paper.brand)
#         print(paper.description)
#         print(paper.size())