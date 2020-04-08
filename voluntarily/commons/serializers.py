from voluntarily.extensions import ma


class EmailSchema(ma.ModelSchema):
    address = ma.Str()
    isVerified = ma.Boolean()


class PhoneSchema(ma.ModelSchema):
    number = ma.Str()
    isVerified = ma.Boolean()


class GeoSchema(ma.ModelSchema):
    lat = ma.Decimal()
    lon = ma.Decimal()


class MapViewSchema(ma.ModelSchema):
    west = ma.Decimal()
    south = ma.Decimal()
    east = ma.Decimal()
    north = ma.Decimal()


class AddressSchema(ma.ModelSchema):
    label = ma.Str()
    houseNumber = ma.Str()
    street = ma.Str()
    district = ma.Str()
    city = ma.Str()
    county = ma.Str()
    state = ma.Str()
    postalCode = ma.Str()
    countryCode = ma.Str()
    countryName = ma.Str()


class HereResultSchema(ma.ModelSchema):
    title = ma.Str()
    id_ = ma.Str()
    resultType = ma.Str()
    houseNumberType = ma.Str()
    position = ma.Nested(GeoSchema)
    address = ma.Nested(AddressSchema)
    access = ma.List(ma.Nested(GeoSchema))
    mapView = ma.Nested(MapViewSchema)
    userInput = ma.Str()


class HashtagSchema(ma.ModelSchema):
    name = ma.Str()
    isVerified = ma.Boolean()
    isRequired = ma.Boolean()


class GiveOfferSchema(ma.ModelSchema):
    name = ma.Str()
    totalSlots = ma.Int()
    availableSlots = ma.Int()
    assignedSlots = ma.Int()


class UserSchema(ma.ModelSchema):
    userId = ma.Int()
    role = ma.Str()
    name = ma.Str()
    screenname = ma.Str()
    email = ma.Nested(EmailSchema)
    phone = ma.Nested(PhoneSchema)
    location = ma.Nested(HereResultSchema)
    biography = ma.Str()
    freeNotes = ma.Str()
    imageUrls = ma.List(ma.Str())
    otherUrls = ma.List(ma.Str())
    criticalCategories = ma.List(ma.Str())
    hashtags = ma.List(ma.Nested(HashtagSchema))
    giveOffers = ma.List(ma.Nested(GiveOfferSchema))
    isFirstResponder = ma.Boolean()
    stillHaveToPhysicallyGoToWork = ma.Boolean()
    redFlag = ma.Boolean()
    lastUpdated = ma.Str()
    createdAt = ma.Str()


class UserListSchema(ma.ModelSchema):
    users = ma.List(ma.Nested(UserSchema))


class SearchSchema(UserSchema):
    locationType = ma.Str()
    distance = ma.Str(default="10mi")
    ignoreFields = ma.List(ma.Str())
    requiredFields = ma.List(ma.Str())
    from_ = ma.Int(default=0)
    size = ma.Int(default=10)


class NeedClusterSchema(ma.ModelSchema):
    userRequestedLimit = ma.Int()
    adminRequestedLimit = ma.Int()
    numberOfAssignedGivers = ma.Int()
    remainingGiversNeeded = ma.Int()


class NeedSchema(ma.ModelSchema):
    userId = ma.Int()
    needRequestName = ma.Str()
    address = ma.Nested(HereResultSchema)
    totalSlots = ma.Int()
    matchedGivers = ma.List(ma.Int())
    hashtags = ma.List(ma.Nested(HashtagSchema))
    cluster = ma.Nested(NeedClusterSchema)
    priority = ma.Int()

class NeedListSchema(ma.ModelSchema):
    needs = ma.List(ma.Nested(NeedSchema))