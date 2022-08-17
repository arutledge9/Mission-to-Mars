# refactored from "scraping_prefunctionizing.py"


#import splinter/beautiful soup/pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd



# SCRAPE ALL -- initialize browser, create data dict, end WebDriver and return scraped data

def scrape_all():
    #initialize headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_p = mars_news(browser)
    
    #run all scraping functions and store results in dict
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    #stop webdriver and return data
    browser.quit()
    return data

# The DATA dictionary does two things: It runs all of the functions 
# we've created—featured_image(browser), for example—and it also 
# stores all of the results. When we create the HTML template, 
# we'll create paths to the dictionary's values, which lets us 
# present our data on our template. We're also adding the date 
# the code was run last by adding "last_modified": 
# dt.datetime.now(). For this line to work correctly, we'll 
# also need to add import datetime as dt to our imported 
# dependencies at the beginning of our code.


#SCRAPE MARS NEWS
def mars_news(browser):
    # visit mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    #optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #convert browser html to soup obj and quit browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        #use parent element to find the first <a> tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        #use the parent element to find the article summary paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


### HEMISPHERE IMAGES


def hemispheres(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    hemisphere_image_urls = []
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    
    main = hemi_soup.find_all('h3')[0:4]

    for hemi in main:
        hemispheres = {}
        page = browser.find_by_text(hemi.text)
        page.click()
        html = browser.html
        yo_soup = soup(html, 'html.parser')
        dwnld = yo_soup.find('div', class_='downloads')
        a = dwnld.find('a', target='_blank')
        href = a['href']
        img_url = f'https://marshemispheres.com/{href}'
        pretitle = yo_soup.find('div', class_='cover')
        title = pretitle.find('h2').get_text()
        hemispheres['URL'] = img_url
        hemispheres['Title'] = title
        hemisphere_image_urls.append(hemispheres)
        browser.back()
    
    return hemisphere_image_urls


### FEATURED IMAGE

def featured_image(browser):
    #visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        #find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url


# MARS FACTS

def mars_facts():
    #use 'read-html' to scrape the facts table into a DF
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # assign columns and set indec of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # dataframe to html, add bootstrap
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":
    # if running as script, print scraped data
    print(scrape_all())

