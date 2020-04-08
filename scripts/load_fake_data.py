import random
import json
from faker import Faker
from faker.providers import geo, lorem, internet
from elasticsearch import Elasticsearch

fake = Faker()
fake.add_provider(geo)
fake.add_provider(lorem)
fake.add_provider(internet)

base_user_profile = {
    "userId": 124,
    "role": "giver",
    "name": "Joe Smith",
    "screenname": "joesmith",
    "email": {
        "address": "joesmith@gmail.com",
        "isVerified": True
    },
    "phone": {
        "number": "(406) 555-1212",
        "isVerified": True
    },
    "location": {
        "title": "1623 SW Spring Garden St, Portland, OR 97219-4284, United States",
        "resultType": "houseNumber",
        "houseNumberType": "PA",
        "address": {
            "label": "1623 SW Spring Garden St, Portland, OR 97219-4284, United States",
            "countryCode": "USA",
            "countryName": "United States",
            "state": "Oregon",
            "county": "Multnomah",
            "city": "Portland",
            "district": "South Burlingame",
            "street": "SW Spring Garden St",
            "postalCode": "97219-4284",
            "houseNumber": "1623"
        },
        "position": {
            "lat": 45.4637,
            "lng": -122.69478
        },
        "access": [
            {
                "lat": 45.46347,
                "lon": -122.69477
            }
        ],
        "mapView": {
            "west": -122.69606,
            "south": 45.4628,
            "east": -122.6935,
            "north": 45.4646
        },
        "scoring": {
            "queryScore": 1,
            "fieldScore": {
                "state": 1,
                "city": 1,
                "streets": [
                    1
                ],
                "houseNumber": 1,
                "postalCode": 1
            }
        },
        "id_": "here:af:streetsection:SAmiM5W2ir3fX3HaVKHl.C:CgcIBCCrvewZEAEaBDE2MjMoZA",
        "geo": {
            "lat": 45.4637,
            "lon": -122.69478
        },
        "userInput": "1623 SW Spring Garden St, Portland, OR, 97219"
    },
    "biography": "I am a good person.",
    "freeNotes": "This person is a good person.",
    "imageUrls": [],
    "otherUrls": [],
    "criticalCategories": [],
    "hashtags": [],
    "giveOffers": [],
    "isFirstResponder": True,
    "stillHaveToPhysicallyGoToWork": True,
    "redFlag": False,
    "lastUpdated": "2020-04-01T22:14:23.195447",
    "createdAt": "2020-04-01T22:14:23.195449"
}

coordinates = []
with open('ohio_geo.json') as fh:
    for line in fh:
        geo = json.loads(line)
        coordinates.append(geo)

roles = [
    "giver",
    "getter",
    "both"
]
give_offers = [
    "phoneSupport",
    "groceryDelivery",
    "childcare",
    "medical",
    "checkins",
    "therapy",
    "programming",
    "pets",
    "NoCurrentNeedButVulnerable",
    "MedicationPickup",
    "NeedBackupBecauseSmallLocakNetwork",
    "MentalHealthCounseling",
    "NavigatingBureacracy",
    "ApplyingForUnemploymentOrAid",
    "LocalOrganizing",
    "HelpWithTech",
    "AnythingAndEverything"
]

hashtags = [
    "lgbtq",
    "spanish",
    "french",
    "german",
    "english",
    "japanese",
    "minority",
    "spiritual",
    "pregnant",
    "nurse",
    "teacher",
    "over60",
    "over70",
    "over80",
    "AMEChurch",
    "Baptist",
    "MormonLDS",
    "Catholic",
    "DogLover",
    "CatLover",
    "IsolatedFromFamily",
    "LowIncome",
    "rural"
]

critical_categories = [
    "nurseDocMed",
    "elderly",
    "immunoCompromised",
    "disability",
    "veryIsolated",
    "lowIncome"
]

es = Elasticsearch()

index_body = {
    "mappings": {
        "properties" : {
            "location" : {
                "properties" : {
                    "geo": {
                        "properties": {
                            "type": "geo_point"
                        }
                    }
                }
            }
        }
    }
}

es.indices.create('needs', body=index_body, ignore=400)
es.indices.create('users', body=index_body, ignore=400)

def generate_user(user_id, user_type):
    user = base_user_profile
    user_role = fake.words(nb=1, ext_word_list=roles, unique=True)[0]
    user_hashtags = []
    for _ in range(0, random.randint(1,5)):
        user_hashtags.append({
            "name": fake.words(nb=1, ext_word_list=hashtags, unique=True),
            "isVerified": bool(random.getrandbits(1)),
            "isRequired": bool(random.getrandbits(1))
        })
    user_give_offers = []
    if user_role in ['giver', 'both']:
        for _ in range(0, random.randint(1,5)):
            total_slots = random.randint(1,5)
            user_give_offers.append({
                "name": fake.words(nb=1, ext_word_list=give_offers, unique=True),
                "totalSlots": total_slots,
                "availableSlots": total_slots,
                "assignedSlots": 0
            })
    user_critical_categories =  fake.words(nb=random.randint(0,5), ext_word_list=critical_categories, unique=True)
    user_address_data = random.choice(coordinates)
    user.update({
        "userId": user_id,
        "name": fake.name(),
        "role": user_role,
        "email": {
            "address": fake.email(),
            "isVerified": bool(random.getrandbits(1))
        },
        "phone": {
            "number": fake.phone_number(),
            "isVerified": bool(random.getrandbits(1))
        },
        "giveOffers": user_give_offers,
        "hashtags": user_hashtags,
        "criticalCategories": user_critical_categories,
        "location": {
            "address": {
                "postalCode": user_address_data["zip"]
            },
            "geo": {
                "lat": user_address_data["lat"],
                "lon": user_address_data["lon"],
            }
        },
        "isFirstResponder": bool(random.getrandbits(1)),
        "stillHaveToPhysicallyGoToWork": bool(random.getrandbits(1)),
    })
    return user


def generate_need(user_id):
    user_hashtags = []
    for _ in range(0, random.randint(1,5)):
        user_hashtags.append({
            "name": fake.words(nb=1, ext_word_list=hashtags, unique=True),
            "isVerified": bool(random.getrandbits(1)),
            "isRequired": bool(random.getrandbits(1))
        })
    user_address_data = random.choice(coordinates)
    userRequestedLimit = random.randint(1,5)
    adminRequestedLimit = random.randint(1,5)
    return {
        "userId": user_id,
        "needRequestName": fake.words(nb=1, ext_word_list=give_offers, unique=True),
        "totalSlots": random.randint(1,5),
        "location": {
            "address": {
                "postalCode": user_address_data["zip"]
            },
            "geo": {
                "lat": user_address_data["lat"],
                "lon": user_address_data["lon"],
            }
        },
        "hashtags": user_hashtags,
        "matchedGivers": [],
        "cluster": {
            "userRequestedLimit": userRequestedLimit,
            "adminRequestedLimit": adminRequestedLimit,
            "assigned": 0,
            "remainingNeeded": userRequestedLimit
        },
        "priority": random.randint(1,5)
    }
    return body


# GIVERS - Have abilities
for user_id in range(0, 25000):
    body = generate_user(user_id, 'giver')
    es.index('users', id=user_id, body=body)

# Getters - No abilities
for user_id in range(25000, 50000):
    user_body = generate_user(user_id, 'getter')
    es.index('users', id=user_id, body=user_body)
    for _ in range(0, random.randint(1,4)):
        need_body = generate_need(user_id)
        es.index('needs', body=need_body)