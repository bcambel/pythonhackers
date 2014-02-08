import collections
from datetime import datetime as dt
import hashlib
import base64
import logging
import sys
import pprint
from time import mktime
import uuid
import os
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy import or_, and_
from pyhackers.sentry import sentry_client as error_reporter
from pyhackers.common.timelimit import timelimit, TimeoutError
from pyhackers.common.stringutils import safe_str, max_length_field, non_empty_str, safe_filename
from pyhackers.db import DB as session


pp = pprint.PrettyPrinter(indent=6)
default_timeout_limit = 30
current_timeout = default_timeout_limit
content_attributes = ['language', 'value', 'type']
entry_attributes = ['author', 'feedburner_origlink', 'id', 'href', 'published_parsed', 'updated_parsed', 'tags',
                    'title', 'link', 'media_content', 'media_thumbnail']
feed_attributes = ['title', 'language', 'description', 'href', 'updated_parsed', 'version', 'author', 'link']
general_attributes = ['etag', 'status']


class Post:
    id = 0


class Feed:
    id = 0


class FeedHistory:
    id = 0


def test(url):
    get_feed(url)


code_status_results = {
    0: "?",
    2: "DONE",
    3: "MOVED",
    4: "NF",
    5: "ERROR"
}


def task(name, args):
    pass


def get_feed(rss_url, stats=False):
    post_ids = []

    try:
        for o in download_feed_return_objects(rss_url):
            if o is None:
                continue
            if isinstance(o, Post):
                post_ids.append(o.id)
            session.add(o)
        try:
            if len(post_ids):
                session.commit()
        except Exception, ex:
            session.rollback()
            error_reporter.captureException()
            logging.exception(ex)
            return False

        if len(post_ids) > 0:
            logging.info("Saved %d posts for %s" % (len(post_ids), safe_str(rss_url)))
        else:
            logging.info("No Posts saved for %s" % safe_str(rss_url))

        for id in post_ids:
            if stats:
                task('get_post_stats', args=(str(id),)).apply_async()
            task('index_post', args=(str(id),)).apply_async()

    except Exception, ex:
        error_dict = {"rss_url": safe_str(rss_url)}

        logging.warn("{0}Exception Occured:{1}{0}".format((20 * "="), ex.message))
        try:
            error_reporter.captureException(**error_dict)
        except Exception, error_reporter_exception:
            print error_reporter_exception


def url_hash(url):
    return base64.urlsafe_b64encode(hashlib.md5(safe_str(url)).digest())


def rss_exists(url):
    rss_hash = url_hash(url)
    feed = None

    try:
        feed = session.query(Feed).filter_by(rss_hash=rss_hash).first()
    except:
        error_reporter.captureException()
        try:
            session.rollback()
        except:
            error_reporter.captureException()
        raise

    return feed


def fix_lang_str(lang):
    if len(lang) > 3:
        if '-' in lang:
            lang = lang.split('-')[0]
        else:
            lang = lang[:3]
    return lang


def create_new_feed(feed_parser_results, rss_url):
    feed_obj = Feed()
    feed_obj.id = uuid.uuid1()

    feed_obj.rss = rss_url
    feed_obj.href = feed_parser_results.get("href", "") or ""
    feed_obj.link = feed_parser_results.get("link", "") or ""
    feed_obj.description = feed_parser_results.get("description", "") or ""
    feed_obj.author = feed_parser_results.get("author", "") or ""
    feed_obj.version = feed_parser_results.get("version", "") or ""
    feed_obj.active = True

    max_length_field(feed_obj, "title", 100)

    feed_obj.lang = fix_lang_str(feed_parser_results.get("language", 'en') or 'en')

    feed_obj.rss_hash = url_hash(rss_url)
    return feed_obj


def find_existing_posts(feed_id, post_id_hashes, post_link_hashes):
    try:

        return session.query(Post.post_id_hash, Post.link_hash).filter(
            and_(
                Post.feed_id == feed_id,
                or_(
                    Post.post_id_hash.in_(post_id_hashes),
                    Post.link_hash.in_(post_link_hashes),
                )
            )
        )
    except:
        session.rollback()
        error_reporter.captureException()
        return None


def find_feed_status_from_scode(feed_obj):
    code = int(str(feed_obj.status_code)[0])
    if code_status_results.has_key(code):
        return code_status_results[code]
    else:
        return code_status_results[0]


def cut_clean_etag(etag, max_len=50):
    if etag is not None:
        etag = etag.replace('"', '')
        if len(etag) > max_len:
            etag = etag[:max_len]
        return etag
    else:
        return ""


def download_feed_return_objects(rss_url):
    try:
        feed_obj = rss_exists(rss_url)
    except:
        yield None
        return

    feed_obj_found = False
    feed_parser_results, success = get_rss(rss_url)

    if feed_parser_results is None:
        error_reporter.captureMessage('Feed Parser results is None', **dict(rss_url=rss_url))
        yield None
        return

    if feed_obj is None:
        feed_obj = create_new_feed(feed_parser_results, rss_url)
    else:
        feed_obj_found = True

    feed_id = feed_obj.id
    feed_obj.title = feed_parser_results.get("title", "") or ""
    max_length_field(feed_obj, 'title', 100)

    feed_obj.status_code = feed_parser_results.get("status", "") or 200
    feed_obj.status = find_feed_status_from_scode(feed_obj)

    feed_obj.etag = cut_clean_etag(feed_parser_results.get("etag", ""))

    updated_date = feed_parser_results.get("updated_parsed")
    feed_obj.updated = dt.fromtimestamp(mktime(updated_date)) if updated_date is not None else dt.utcnow()
    #	feed_obj.published =  dt.fromtimestamp(mktime(published_date)) if published_date is not None else None
    feed_obj.last_check = dt.utcnow()

    # We could be creating a new feed, or updating the existing one.
    yield feed_obj
    rss_posts = []

    for feed_article in feed_parser_results.get("entries", []):
        ptime = feed_article.get("published_parsed", None)
        post_date = dt.fromtimestamp(mktime(ptime)) if ptime is not None else dt.utcnow()
        #		print "%r" % post
        p = Post(
            id=uuid.uuid1(),
            title=feed_article.get("title", ""),
            author=feed_article.get("author", ""),
            href=feed_article.get("href", ""),
            post_id=feed_article.get("id", ""),
            published_at=post_date,
            feed_id=feed_id
        )

        p.original_title = max_length_field(p, 'title', 200)
        p.original_author = max_length_field(p, 'author', 200)

        p.content_html = feed_article.get("content", "") or ""

        if feed_article.has_key("media_content"):
            media_contents = feed_article.get("media_content", []) or []
            if media_contents is not None and (not isinstance(media_contents, basestring)) and isinstance(
                    media_contents, collections.Iterable):
                p.media = [media.get("url") for media in media_contents]

        hasHash = False

        if feed_article.has_key("feedburner_origlink"):
            p.original_link = feed_article.get("feedburner_origlink", "")
            if non_empty_str(p.original_link):
                p.link_hash = url_hash(safe_str(p.original_link))
                hasHash = True

        if feed_article.has_key("link"):
            p.href = feed_article.get("link", "")
            if not hasHash and non_empty_str(p.href):
                p.link_hash = url_hash(safe_str(p.href))
                hasHash = True

        if not hasHash:
            print "Post don't have any hash"

        p.title_hash = url_hash(safe_str(p.title)) if non_empty_str(p.title) else ""
        p.post_id_hash = url_hash(safe_str(p.post_id)) if non_empty_str(p.post_id) else ""

        if feed_article.has_key("tags"):
            if isinstance(feed_article['tags'], collections.Iterable):
                p.tags = [pst.get("term") for pst in feed_article['tags']]

        rss_posts.append(p)

    has_posts = len(rss_posts) > 0
    post_id_hashes = [p.post_id_hash for p in rss_posts]
    #	post_title_hashes = [p.title_hash for p in rss_posts]
    post_link_hashes = [p.link_hash for p in rss_posts]

    found_posts_id_hashes = []
    found_posts_link_hashes = []

    if feed_obj_found and has_posts:
        existing_posts = find_existing_posts(feed_id, post_id_hashes, post_link_hashes)

        for ex_post_id_hash, ex_link_hash in existing_posts:
            found_posts_id_hashes.append(ex_post_id_hash)
            found_posts_link_hashes.append(ex_link_hash)

    has_existing_posts = len(found_posts_id_hashes) > 0 or len(found_posts_link_hashes) > 0

    new_post_count = 0
    if has_posts:
        for rss_post in rss_posts:
            should_skip = False

            if has_existing_posts:
                if non_empty_str(rss_post.post_id_hash) and rss_post.post_id_hash in found_posts_id_hashes:
                    should_skip = True
                elif rss_post.link_hash in found_posts_link_hashes:
                    should_skip = True  # "Link Hash found in existing records"

            if not should_skip:
                new_post_count += 1
                #				post_indexer.index(rss_post)
                #				print "%s - %s [SAVE]" % (rss_post.post_id_hash,safe_str(rss_post.title))
                yield rss_post

    feed_history = FeedHistory(id=uuid.uuid1(),
                               feed_id=feed_obj.id,
                               timestamp=dt.utcnow(),
                               status=feed_obj.status_code,
                               post_count=new_post_count,
                               etag=feed_obj.etag)
    yield feed_history


def get_object_attr_values(anyobj):

    if not hasattr(anyobj, '__dict__'):
        yield [None, "Object has No __dict__"]
        return
    else:
        pass

    if isinstance(anyobj, dict):
        obj_val_ref = anyobj
    else:
        obj_val_ref = anyobj.__dict__

    for attr, value in obj_val_ref.iteritems():
        yield (attr, value)




def current_dir(file=__file__):
    return os.path.dirname(os.path.abspath(file))


def parent_dir(file=__file__):
    return os.path.dirname(current_dir(file))


def join_path_with_parent_dir(path, file=__file__):
    return os.path.join(os.path.dirname(parent_dir(file)), path)


def get_current_timeout():
    return current_timeout


@timelimit(get_current_timeout)
def download_rss(url):
    return feedparser.parse(url)





def get_rss(url):
    results = None
    success = False
    feed_parser_inst = None

    try:
        feed_parser_inst = download_rss(url)
        success = True
    except TimeoutError:
        pass
    except (UnicodeEncodeError, Exception):
        error_reporter.captureException(**dict(url=url))

    if success:
        results = extract_rss_results(feed_parser_inst, url=url)
    else:
        print "Url not successfull %s " % safe_str(url)

    return results, success


def extract_rss_results(feed, url=''):
    rss_result = dict(entries=[], **dict([(attr, None) for attr in feed_attributes]))

    for attr in general_attributes:
        if hasattr(feed, attr):
            rss_result[attr] = feed[attr]

    for attr in feed_attributes:
        if hasattr(feed.feed, attr):
            rss_result[attr] = feed.feed[attr]

    debug_feed_object(feed, url_downloaded=url)

    for entry in feed.entries:
        feed_entry = {'content': ''}
        content_html = ""
        if hasattr(entry, "content"):
            content = entry.content
            if isinstance(content, collections.Iterable):
                content_html = content[0].value
            elif isinstance(content, basestring):
                content_html = content
            else:
                error_reporter.captureMessage("Content has weird setup")
                content_html = ''

        if hasattr(entry, "description") and not len(content_html):
            if isinstance(entry.description, basestring):
                content_html = entry.description
            elif isinstance(entry.description, list):
                content_html = entry.description[0]  # its a list!
                if isinstance(content_html, dict):
                    content_html = entry.description[0].value  # it's a list contains a dict
                elif isinstance(content_html, basestring):
                    pass
                else:
                    print "What the fuck is this type? %s " % type(content_html)

        bsoup = BeautifulSoup(content_html)
        html_text = content_html
        if bsoup is not None and len(bsoup.contents) > 0:
            html_text = "".join([c.__unicode__() for c in bsoup.contents])

        feed_entry['content'] = html_text

        for attr in entry_attributes:
            if hasattr(entry, attr):
                val = entry[attr]
                if val is not None and isinstance(val, basestring):
                    bsoup2 = BeautifulSoup(val)
                    val = "".join([c.__unicode__() for c in bsoup2.contents]) if bsoup2 is not None and len(
                        bsoup2.contents) > 0 else val
                    val = val

                feed_entry[attr] = val

        rss_result["entries"].append(feed_entry)

    return rss_result


def debug_feed_object(feed_obj, url_downloaded):
    file_name = safe_filename(url_downloaded)
    if len(file_name) > 100:
        file_name = file_name[:100]

    debug_file = os.path.join(join_path_with_parent_dir(path='logs', file=__file__), (file_name + ".log"))

    with open(debug_file, "w+") as dobj_file:
        for attr, val in get_object_attr_values(feed_obj):
            pprint.pprint((attr, val, type(val)), stream=dobj_file)


if __name__ == "__main__":
    url = sys.argv[1]

    get_rss(url)