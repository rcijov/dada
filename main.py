from bs4 import BeautifulSoup
import urllib.request
from re import findall
from flask import Flask
from flask import render_template
import time

year = time.strftime("%Y")


class ScrapeSite:

    def __init__(self, url):
        self.url = url
        self.data = urllib.request.urlopen(url)
        self.soup = BeautifulSoup(self.data)
        self.body = self.soup.get_text()

    def regex(self, string):
        return findall(string, self.body)

## Reddit ##


class Reddit(ScrapeSite):

    def __init__(self):
        ScrapeSite.__init__(self, 'http://www.reddit.com')

    # Walks through subreddits and returns a dictionary with the subs and how many of each are on the front page
    # "raw" flag for debugging
    def subreddits(self, raw=False):
        subreddits_search = self.soup.find_all(
            "a", class_="subreddit hover may-blank")
        subreddits_regex = findall(r'r\/[a-z]+', str(subreddits_search))
        subreddits_seen = set(subreddits_regex)
        subreddits = {}

        for items in subreddits_seen:
            subreddits[items] = 0

        for items in subreddits_regex:
            if items in subreddits:
                subreddits[items] += 1

        if raw is False:
            return subreddits
        else:
            return subreddits_regex

    # Calculates exactly how cute the front page of Reddit is, based on the
    # number of /r/aww submissions that are present
    def cuteness_index(self):
        cuteness_finder = 0
        subreddits = self.subreddits()
        for items in subreddits:
            if 'aww' in items:
                cuteness_finder = subreddits[items]

        return cuteness_finder

    def cuteness(self, level):
        cuteness_levels = [
            'Filthy sloth.', 'Excited corgi!', 'Kitten euphoria!!!']
        return cuteness_levels[level]

    # Returns all of the images that are currently on the front page
    def images(self):
        return self.soup.find_all("a", class_="thumbnail")

## TechCrunch ##


class TechCrunch(ScrapeSite):

    def __init__(self):
        ScrapeSite.__init__(self, 'http://www.techcrunch.com')

    # Number of times VCs are mentioned on TC's front page
    def VCs(self):
        vc_word_search = self.regex(r'(?:VC[s]?|[Vv]enture [Cc]apital[ist]?)')
        return len(vc_word_search)

    # Measures how disruptive, innovative and/or Twittergasmic TC is at the
    # time
    def disruption(self, level):
        disruption_levels = [
            '2014 MySpace.', 'Getting Googley!', 'Twittergasm!!!']
        return disruption_levels[level]

    # Shows who is getting articles published on the front page of TC
    def writers(self, raw=False):
        writers_regex = self.soup.find_all('a', {"rel": "author"})
        writers_list = []
        writers_seen = set()

        for authors in writers_regex:
            writers_list.append(authors.get_text())
            writers_seen.add((authors.get_text(), authors.get('href')))

        writers = {}

        for authors in writers_seen:
            writers[authors] = 0

        for authors in writers_regex:
            if authors.get_text() in writers_list:
                writers[authors.get_text(), authors.get('href')] += 1

        if raw is False:
            return writers

        else:
            return writers_regex

# Instances
RedditScraper = Reddit()
TCScraper = TechCrunch()

## Site ##
tagline = "Scraping only the finest data"

app = Flask(__name__)
title = 'aloha'


@app.context_processor
def site_info():
    return {'title': title, 'tagline': tagline, 'year': year}


@app.route('/')
def front_page():
    return render_template('index.html',
                           subreddits=RedditScraper.subreddits(),
                           images=RedditScraper.images(),
                           VCs=TCScraper.VCs(),
                           disruption_levels=TCScraper.disruption,
                           cuteness_levels=RedditScraper.cuteness,
                           cuteness_index=RedditScraper.cuteness_index(),
                           writers=TCScraper.writers())

if __name__ == '__main__':
    app.run(debug=True)
