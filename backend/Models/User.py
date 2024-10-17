import json

class User():
    firstName = None
    lastName = None
    password = None
    address = None
    username = None
    country = None
    phoneNumber = None
    email = None

     #konsutrktor sa poljima
    def __init__(self, fist_name, last_name, password, address, username, country, phone_number, email):
        self.firstName = fist_name
        self.lastName = last_name
        self.address = address
        self.password = password
        self.username = username
        self.country = country
        self.phoneNumber = phone_number
        self.email = email


def ListToDict(list):
    dict={
        "id":list[0],
        "firstName":list[1],
        "lastName":list[2],
        "address":list[3],
        "country":list[4],
        "username":list[5],
        "password":list[6],
        "phoneNumber":list[7],
        "email":list[8],
        "loggedIn":list[9],
        "likedTopic":json.loads(list[10]),
        "unlikedTopic":json.loads(list[11]),
        "likedComment":json.loads(list[12]),
        "unlikedComment":json.loads(list[13]),
        "interests":json.loads(list[14])
    }
    return dict

