from html.parser import HTMLParser

from dateutil import parser
from slugify import slugify

from const import *
from local_secrets import SECRETS_CONTACT_EMAIL


def format_form_response_to_dataset(body):
    title = body.get(TITLE, "")
    return {
        "identifier": slugify(title),
        "datasetVersion": {
            "metadataBlocks": {
                "citation": {
                    "displayName": "Citation Metadata",
                    "fields": [
                        {
                            "typeName": "title",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": title
                        },
                        {
                            "typeName": "subtitle",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get(SUBTITLE, "")
                        },
                        {
                            "typeName": "alternativeTitle",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get(ALTERNATIVE_TITLE, "")
                        },
                        {
                            "typeName": "alternativeURL",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get(ALTERNATIVE_URL, "")
                        },
                        {
                            "typeName": "author",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{
                                "authorName": {
                                    "typeName": "authorName",
                                    "multiple": False,
                                    "typeClass": "primitive",
                                    "value": body.get(AUTHOR_NAME, "")
                                }
                            }]
                        },
                        {
                            "typeName": "datasetContact",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{
                                "datasetContactEmail": {
                                    "typeName": "datasetContactEmail",
                                    "multiple": False,
                                    "typeClass": "primitive",
                                    "value": SECRETS_CONTACT_EMAIL
                                }
                            }]
                        },
                        {
                            "typeName": "dsDescription",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{
                                "dsDescriptionValue": {
                                    "typeName": "dsDescriptionValue",
                                    "multiple": False,
                                    "typeClass": "primitive",
                                    "value": desc_
                                }
                            } for desc_ in [
                                body.get(DS_DESCRIPTION_VALUE_UA, ""),
                                body.get(DS_DESCRIPTION_VALUE_EN, "")
                            ] if desc_ != ""]
                        },
                        {
                            "typeName": "subject",
                            "multiple": True,
                            "typeClass": "controlledVocabulary",
                            "value": [
                                "Law", "Social Sciences", "Other"
                            ]
                        },
                        {
                            "typeName": "keyword",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{
                                "keywordValue": {
                                    "typeName": "keywordValue",
                                    "multiple": False,
                                    "typeClass": "primitive",
                                    "value": keyword_
                                }
                            } for keyword_ in body.get(KEYWORD, "").split(", ")]
                        },
                        {
                            "typeName": "depositor",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get(DEPOSITOR, "")
                        },
                        {
                            "typeName": "dateOfDeposit",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": parser.parse(body.get(DATE_OF_DEPOSIT)).strftime("%Y-%m-%d")
                            if body.get(DATE_OF_DEPOSIT) else ""
                        },
                        {
                            "typeName": "language",
                            "multiple": True,
                            "typeClass": "controlledVocabulary",
                            "value": [
                                "Ukrainian"  # body.get(LANGUAGE, "")
                            ]
                        },
                        {
                            "typeName": "kindOfData",
                            "multiple": True,
                            "typeClass": "primitive",
                            "value": [
                                body.get(KIND_OF_DATA, "")
                            ]
                        },
                        {
                            "typeName": "originOfSources",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get(ORIGIN_OF_SOURCES, "")
                        },
                        {
                            "typeName": "distributionDate",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": parser.parse(body.get(DISTRIBUTION_DATE)).strftime("%Y-%m-%d")
                            if body.get(DISTRIBUTION_DATE) else ""
                        },
                        {
                            "typeName": "notesText",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get(NOTES_TEXT, "")
                        },
                    ]
                },
                "geospatial": {
                    "displayName": "Geospatial Metadata",
                    "fields": [
                        {
                            "typeName": "geographicCoverage",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{
                                "otherGeographicCoverage": {
                                    "typeName": "otherGeographicCoverage",
                                    "multiple": False,
                                    "typeClass": "primitive",
                                    "value": body.get(OTHER_GEOGRAPHIC_COVERAGE, "")
                                }
                            }]
                        }
                    ]
                }
            }
        }
    }


class MyHTMLParser(HTMLParser):
    links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links += [attr[1] for attr in attrs if attr[0] == "href"]
