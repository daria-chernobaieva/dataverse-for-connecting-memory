from dateutil import parser
from slugify import slugify


def format_form_response_to_dataset(body):
    title = body["Назва джерела"]
    return {
        "authority": "anAuthority",
        "identifier": slugify(title),
        "persistentUrl": "http://dx.doi.org/10.5072/FK2/9",
        "protocol": "chadham-house-rule",
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
                            "value": body["Назва англійською"]
                        },
                        {
                            "typeName": "alternativeTitle",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body["Назва файлу з джерелом"]
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
                                    "value": body["Автор джерела"]
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
                                    "value": "daria.chernobaieva@gmail.com"
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
                            } for desc_ in [body["Опис українською"], body["Опис англійською (за можливості)"]]]
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
                            } for keyword_ in body["Ключові слова"].split(", ")]
                        },
                        {
                            "typeName": "publication",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{
                                "publicationURL": {
                                    "typeName": "publicationURL",
                                    "multiple": False,
                                    "typeClass": "primitive",
                                    "value": body["Інтернет посилання (для онлайн джерела)"]
                                }
                            }]
                        },
                        {
                            "typeName": "depositor",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body["Хто подав джерело до проєкту"]
                        },
                        {
                            "typeName": "dateOfDeposit",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": parser.parse(body["Дата подання джерела до проєкту"]).strftime("%Y-%m-%d")
                        },
                        {
                            "typeName": "language",
                            "multiple": True,
                            "typeClass": "controlledVocabulary",
                            "value": [
                                "Ukrainian"  # body["Мова джерела"]
                            ]
                        },
                        {
                            "typeName": "kindOfData",
                            "multiple": True,
                            "typeClass": "primitive",
                            "value": [
                                body[
                                    "Вид джерела (пост в соцмережах, стаття, новини, офіційне звернення, відеоматеріал, графічне зображення, фото, тощо)"]
                            ]
                        },
                        {
                            "typeName": "originOfSources",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body["Звідки взято джерело (сайт, фейсбук, приватне фото, тощо)"]
                        },
                        {
                            "typeName": "distributionDate",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": parser.parse(body["Дата публікації джерела "]).strftime("%Y-%m-%d")
                        },
                        {
                            "typeName": "notesText",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body["Офіційний переклад англійською за наявності"]
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
                                    "value": body["Місцевість (місцевості), згадані у джерелі"]
                                }
                            }]
                        }
                    ]
                }
            }
        }
    }
