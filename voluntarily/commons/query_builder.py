from voluntarily.extensions import es, geocoder

def build_query(body):
    query = {
        "query": {
            "bool": {
                "must": [
                ]
            }
        },
        "highlight": {
            "fields": {
                "tags": {
                    "type": "plain"
                },
                "needName": {
                    "type": "plain"
                }
            }
        },
        "from": body.get('from', 0),
        "size": body.get('size', 30)
    }

    ignore_fields = body.get("ignore", [])
    user_id = body.get('userId')
    if user_id and user_id not in ignore_fields:
        query["query"]["bool"]["must"].append(
            {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "userId": user_id
                            }
                        }
                    ]
                }
            }
        )

    # Can be one of the following:
    # 1. Radius of a geo point -> geoRadius,
    # 2. Radius of a zip code -> zipRadius, ?? TODO: Possibly add
    # 3. In the zip code -> zipMatch
    location = body.get("location")
    location_type = body.get("locationType")
    if location:
        if location_type == "radius":
            lat = location.get("geo", {}).get("lat")
            lon = location.get("geo", {}).get("lon")
            if lat and lon and "geo" not in ignore_fields:
                lat = body.get('lat')
                lon = body.get('lon')
                if lat and lon:
                    distance = body.get('distance', '10mi')
                    query["query"]["bool"]["filter"] = {
                        "geo_distance": {
                            "distance": distance,
                            "geo": {
                                "lat": lat,
                                "lon": lon
                            }
                        }
                    }
            else:
                address = location.get("address", {})
                if address:
                    geocode_query = {
                        "postalCode": address.get("postalCode"),
                        "countryCode": address.get("countryCode"),
                        "state": address.get("state"),
                        "city": address.get("city")
                    }
                    geocode_query_filtered = {k: v for k, v in geocode_query.items() if v is not None}
                    geocode_result = geocoder.geocode_address_components(**geocode_query_filtered)
                    if geocode_result:
                        distance = body.get('distance', '10mi')
                        query["query"]["bool"]["filter"] = {
                            "geo_distance": {
                                "distance": distance,
                                "geo": {
                                    "lat": geocode_result[0]['_source']['lat'],
                                    "lon": geocode_result[0]['_source']['lon']
                                }
                            }
                        }
        elif location_type == "match":
            address = location.get("address", {})
            if address:
                postal_code = address.get("postalCode")
                country_code = address.get("countryCode")
                city = address.get("city")
                state = address.get("state")
                if postal_code and "postalCode" not in ignore_fields:
                    query["query"]["bool"]["must"].append({
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "location.address.postalCode": postal_code
                                    }
                                }
                            ]
                        }
                    })
                if country_code and "countryCode" not in ignore_fields:
                    query["query"]["bool"]["must"].append({
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "location.address.countryCode": country_code
                                    }
                                }
                            ]
                        }
                    })
                if city and "city" not in ignore_fields:
                    query["query"]["bool"]["must"].append({
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "location.address.city": city
                                    }
                                }
                            ]
                        }
                    })
                if state and "state" not in ignore_fields:
                    query["query"]["bool"]["must"].append({
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "location.address.state": state
                                    }
                                }
                            ]
                        }
                    })
    hashtags = body.get("hashtags")
    if hashtags and "hashtags" not in ignore_fields:
        tag_query = {
            "bool": {
                "must": [],
                "should": []
            }
        }
        must_tags = [x["name"] for x in hashtags if x["isRequired"]]
        should_tags = [x["name"] for x in hashtags if not x["isRequired"]]
        for tag in must_tags:
            tag_query["bool"]["must"].append(
                {
                    "match": {
                        "hashtags.name": tag
                    }
                }
            )
        if should_tags:
            tag_query["bool"]["should"].append(
                {
                    "terms": {
                        "hashtags.name": should_tags
                    }
                }
            )
        query["query"]["bool"]["must"].append(tag_query)

    needs = body.get('giveOffers')
    if needs and "needs" not in ignore_fields:
        need_query = {
            "bool": {
                "should": []
            }
        }
        needs = [need["name"] for need in needs]
        if needs:
            need_query["bool"]["should"].append(
                {
                    "terms": {
                        "needRequestName": needs
                    }
                }
            )
            query["query"]["bool"]["must"].append(need_query)

    matched_givers = body.get('matchedGivers')
    if matched_givers:
        matched_query = {
            "bool": {
                "must": []
            }
        }
        for user_id in matched_givers:
            matched_query["bool"]["must"].append({
                {
                    "match": {
                        "matchedGivers": user_id
                    }
                }
            })
        query["query"]["bool"]["must"].append(matched_query)

    need_request_name = body.get("needRequestName")
    if need_request_name:
        query["query"]["bool"]["must"].append(
            {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "needRequestName": need_request_name
                            }
                        }
                    ]
                }
            }
        )


    need_priority = body.get("needPriority")
    if need_priority:
        query["query"]["bool"]["must"].append(
            {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "needPriority": need_request_name
                            }
                        }
                    ]
                }
            }
        )

    critical_categories = body.get("criticalCategories")
    if critical_categories:
        query["query"]["bool"]["must"].append({
            "bool": {
                "should": {
                    "terms": {
                        "criticalCategories": critical_categories
                    }
                }
            }
        })

    return query