from src.utils import MyHTMLParser


def test_parse_html_links():
    parser = MyHTMLParser()
    assert parser.links == []

    # no tags
    parser2 = MyHTMLParser()
    parser2.feed("")
    assert parser2.links == []

    # other tags
    parser3 = MyHTMLParser()
    parser3.feed("<html><head></head></html")
    assert parser3.links == []

    # other tag attributes
    parser4 = MyHTMLParser()
    parser4.feed("<a class='test'></a")
    assert parser4.links == []

    # right tag, right tag attribute
    parser5 = MyHTMLParser()
    parser5.feed("<a href='http://test.com'></a")
    assert parser5.links == ["http://test.com"]
