from dateutil import parser
from slugify import slugify

from local_secrets import SECRETS_CONTACT_EMAIL


def format_form_response_to_dataset(body):
    title = body.get("Назва джерела", "")
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
                            "value": body.get("Назва англійською", "")
                        },
                        {
                            "typeName": "alternativeTitle",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get("Назва файлу з джерелом", "")
                        },
                        {
                            "typeName": "alternativeURL",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get("Інтернет посилання (для онлайн джерела)", "")
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
                                    "value": body.get("Автор джерела", "")
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
                            } for desc_ in [body.get("Опис українською", ""), body.get("Опис англійською (за можливості)", "")]]
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
                            } for keyword_ in body.get("Ключові слова", "").split(", ")]
                        },
                        {
                            "typeName": "depositor",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get("Хто подав джерело до проєкту", "")
                        },
                        {
                            "typeName": "dateOfDeposit",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": parser.parse(body.get("Дата подання джерела до проєкту")).strftime("%Y-%m-%d")
                            if body.get("Дата подання джерела до проєкту") else ""
                        },
                        {
                            "typeName": "language",
                            "multiple": True,
                            "typeClass": "controlledVocabulary",
                            "value": [
                                "Ukrainian"  # body.get("Мова джерела", "")
                            ]
                        },
                        {
                            "typeName": "kindOfData",
                            "multiple": True,
                            "typeClass": "primitive",
                            "value": [
                                body.get(
                                    "Вид джерела (пост в соцмережах, стаття, новини, офіційне звернення, відеоматеріал, графічне зображення, фото, тощо)", ""
                                )
                            ]
                        },
                        {
                            "typeName": "originOfSources",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get("Звідки взято джерело (сайт, фейсбук, приватне фото, тощо)", "")
                        },
                        {
                            "typeName": "distributionDate",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": parser.parse(body.get("Дата публікації джерела")).strftime("%Y-%m-%d")
                            if body.get("Дата публікації джерела") else ""
                        },
                        {
                            "typeName": "notesText",
                            "multiple": False,
                            "typeClass": "primitive",
                            "value": body.get("Офіційний переклад англійською за наявності", "")
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
                                    "value": body.get("Місцевість (місцевості), згадані у джерелі", "")
                                }
                            }]
                        }
                    ]
                }
            }
        }
    }
