from flask import Flask, request, make_response
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import json
from CustomClass import JSONEncoder
from flask import jsonify
import pdb


app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
database = app.db = client.trip_planner_development
rounds = app.bcrypt_rounds = 5
api = Api(app)


class User(Resource):
    def post(self):
        requested_json = request.json
        # We have a holder for the json requested data
        # We also need the data that the user essentially wants us to send back
        collection_of_posts = database.posts

        '''Now that we have the document we have to check the neccesary document and see if it has the neccesary crede
        ntials '''

        # So essentially we are going to send the passwords hashed to the database
        # First we have to declare how many times we want to run the encryption algorithm therefore we choose five
        # We have declared the number of rounds above

        # Essentially from there what we do is we take the password in the requested.json and then from there we can encode
        # password in plain text
        # But first we need the password from the json data
        user_password = requested_json.get('password')
        encoded_password = user_password.encode('utf-8')
        hashed = bcrypt.hashpw(encoded_password, bcrypt.gensalt(rounds))
        requested_json['password'] = hashed


        print(hashed)
        # So it is hashing the password therefore we have to find a way to insert this as the password instead of reg string as the password

        if 'username' in requested_json and 'email' in requested_json and 'password' in requested_json:
            collection_of_posts.insert_one(requested_json)
            requested_json.pop('password')

            print('The document has been implemented')
            # pdb.set_trace()
            return(requested_json, 201, None)
        else:
            print('This document could not be inserted into our database')
            return(None, 404, None)

    def get(self):
            # The function that ill be fetching our resources from the database
            # So we need access to the database and collection_
            pdb.set_trace()
            collection_of_posts = app.db.posts

            # Let us get access to our other collection to return all the data all at once

            # Now that we have the collection lets fetch some resources
            #  We have to get the arguments of the users credentialls

            user_email = request.args.get('email')
            user_password = request.args.get('password')
        # And the reason that we have to use get because it is getting the raw value  for the string

            # So essentially what we have to do now is that we have to
            # figure out a way to extract that data back into the plain text
            # back into a plain text

            # So we have access to the collection now
            # And we also have access to finding the document


            # since then emails are unique we will use them as our fetching tool
            user_find = collection_of_posts.find_one({"email": user_email})
            encoded_password = user_password.encode('utf-8')

            # # Now we have to do some error handling
            # if user_find is None:
            #     print('Sorry the user can not be found')
            #     return(None, 404,None)
            # elif user_find is not None:
            #     return(user_find, 200, None)
            #     '''The difference between returning user email and user find is that if we just return user email when we get back the json object
            #     from our database we literally just get back the email but if we were to use user find we can get back the whole document'''
            '''So essentially the error handling that we are doing now compared to the error
            handling we  have above is more solid because now we are essentially making our client which is password
            we are essentially making it we can only retrieve the results if the passwords math'''
            if bcrypt.checkpw(encoded_password, user_find['password']):
                user_find.pop('password')
                print('The user has successfully signed in')
                return(user_find, 200, None)
            else:
                print('The user cannot be found')
                return(None, 401, None)
    def put(self):
        # This function is what essentially edits the resources
        # This function is what essentially edits the resources

        '''So what we are essentially going to need for the function is
        the ability to edit resources therefore we need access to the collection'''
        collection_of_posts = database.posts
        # Now that we have the collection we can no edit the resources

        # This fetching the documents from mongo
        user_email = request.args.get('email')

        # This is getting the raw value for the username from the post request
        user_username = request.json.get('username')

        # Now that we have the two we can common and then from there we can edit the information
        # We now have to locate the document with the specific problems
        user_query = collection_of_posts.find_one({'email': user_email})
        # So now we essentially have access to all the documents with emails in them
        if user_query is None:
            '''Some simple user querying to see if the documents we actually
            are checking contain any information essentially some simple error
            handling'''
            print('Invalid documents sorry!')
            return(None, 404, None)
        elif user_query is not None:
            user_query['username'] = user_username
            collection_of_posts.save(user_query)
            print('The documents have been edited')
            return(user_query, 200, None)

    def delete(self):
        # This is essentially the function to delete users and their accounts
        '''We are going to take the collection find the specific email and remove it
        using the remove method'''

        # Therefore first we have to find the document
        collection_of_posts = database.posts
        # Since we are deleting the user we have to delete the trips that correspond to the email

        collection_of_trips = database.trips
        # Now let us fetch the email from the database as a unique identifier
        user_email = request.args.get('email')

        # Now that we have the email we can delete it using a general query
        user_query = collection_of_posts.find_one({'email': user_email})
        trips_query = collection_of_trips.find_one({'email': user_email})

        # Now we can delete the resources
        if user_query is None and trips_query is None:
            print('The user could not be found to be deleted')
            return(None, 404, None)
        else:
            collection_of_posts.remove(user_query)
            collection_of_trips.remove(trips_query)
            print('The user and their trips have successfully been deleted')
            return(user_query, 204, None)

    def patch(self):
        # So essentially this edits the whole doc as oppose to a singularity

        # So first we need to find the document through a unique identifier
        collection_of_posts = database.posts

        # Now that we have the collection we can now patch the resources
        # By finding the docs with their unique identifier
        user_email = request.args.get('email')

        user_username = request.json.get('email')
        user_username = request.json.get('username')
        user_password = request.json.get('password')
        edited_user_email = request.json.get('email')
        # So now that we have all the neccesary resources we can now patch the docs
        user_query = collection_of_posts.find_one({'email': user_email})

        # Now we implement the error handling
        if user_query is None:
            print('Sorry the document could not be found, therefore could not be patched')
            return(None, 404, None)
        else:
            user_query['email'] = edited_user_email
            user_query['username'] = user_username
            user_query['password'] = user_password
            collection_of_posts.put(user_query)
            print('The existing document has succesfully been patched')
            return(user_query, 200, None)


class Trips(Resource):
    # This is essentially the same as the users class but for the Trips
    def post(self):

        '''So essentially the plan for this function is going to be essentially to post resources but befroe that can even happen
        we have to enure that the user is logged in because then that defies the purpose of posting resources '''
        # This is essentially going to be able to post resource to our trip collection

        # Now we have to get access to the new collection that we are making
        collection_of_trips = database.trips

        # We also need access to the other collection and to do that we need to make a reference
        collection_of_posts = database.posts

        # Now that we have access to the collection we can begin to post the resources
        requested_json = request.json

        # So now we need access to the password and the email in the parmaeters that the network request consists of
        user_email = request.args.get('email')
        user_password = request.args.get('password')

        encoded_password = user_password.encode('utf-8')

        user_account_find = collection_of_posts.find_one({'email': user_email})

        '''So essentially the plan is for us to encode the data and what we have to do is that we have to
        even when the user is posting their trips even though we are not passing in the password what we can essentially do
        is that we can still use that we are making a get request'''

        if 'email' in requested_json and bcrypt.checkpw(encoded_password, user_account_find['password']):
            collection_of_trips.insert_one(requested_json)
            print('The document does have an email address in it')
            return(requested_json, 201, None)
        else:
            print("The document did not contain the email")
            return(None, 404, None)

    def get(self):
        # This function essentially fetches the resources
        # Let us get access to the collection first
        collection_of_trips = database.trips
        collection_of_posts = database.posts
        # Now that we have the collection we can fetch resources by email
        trips_email = request.args.get('email')

        # Remember we are focusing on the parameters becuase they can only fetch if they are logged in
        user_password = request.args.get('password')

        encoded_password = user_password.encode('utf-8')

        # Now that we have the raw value we have to actually see that
        # it is stored within our database
        email_find = collection_of_trips.find_one({'email': trips_email})
        user_password_find = collection_of_posts.find_one({'email': trips_email})

        if bcrypt.checkpw(encoded_password, user_password_find['password']):
            print("The user succesfully fetched their trips")
            return(email_find, 200, None)
        else:
            print('The trips can not be found')
            return(None, 401, None)

    def delete(self):
        # This function will essentially delete resources
        # First we need access to the collection
        collection_of_trips = database.trips
        collection_of_posts = database.posts


        # Then we have to find which document in our database that we have to delete
        requested_email = request.args.get('email')
        requested_password = request.args.get('password')

        encoded_password = requested_password.encode('utf-8')

        # Now that we have the email we have to find the document in our database
        trips_email = collection_of_trips.find_one({'email': requested_email})
        user_account_find = collection_of_posts.find_one({'email': requested_email})

        # Now that we are in the proccess of finding it we have to confirm if the document actually exists
        if trips_email is None:
            print('The document you are trying to delete does not exist')
            return(None, 404, None)
        elif trips_email is not None and bcrypt.checkpw(encoded_password, user_account_find['password']):
            removed_trip = collection_of_trips.remove(trips_email)
            print('The trip has been removed')
            return(removed_trip, 204, None)

    def put(self):
        '''Essentially what this function will do is that it will allow us to be able to edit resources in our document
        however since when a put request is made all the data gets sent back with it therefore what we have to do is that we
        have to whenever the user makes a put request make sure they are editing everything about the trip except their identifier
        which is the email'''

        # first things first we have to get access to the collection
        collection_of_trips = database.trips

        # We are also going to need access to our other collection therefore a reference is in order
        collection_of_posts = database.posts
        # So now that we have the collection we can now specify what the user has to do make a succesfull put request

        # First we have to find the document they want to edit
        requested_email = request.args.get('email')
        trips_query = collection_of_trips.find_one({'email': requested_email})

        requested_password = request.args.get('password')
        encoded_password = requested_password.encode('utf-8')

        user_account_find = collection_of_posts.find_one({'email': requested_email})

        #  We have to take the edited information from the json body they are sending
        print ("request json is: " + str(request.json))
        new_destination = request.json['trips']['destination']
        print ("the destination is: " + str(new_destination))
        new_completed = request.json['trips']['completed']
        new_start_date = request.json['trips']['start_date']
        new_end_date = request.json['trips']['end_date']
        new_waypoint_destination = request.json['trips']['waypoint']['waypoint_destination']
        new_latitude = request.json['trips']['waypoint']['location']['latitude']
        new_longitude = request.json['trips']['waypoint']['location']['latitude']
        # Now that we have seached for the email we have to check if it exists or not
        # if trips_query is None:
        #     print('Couldnot find the document the user is trying to edit')
        #     return(None, 404, None)
        if trips_query is not None and bcrypt.checkpw(encoded_password, user_account_find['password']):
            # So essentially this is the part where we save the changes to our database
                trips_query['trips']['destination'] = new_destination
                trips_query['trips']['completed'] = new_completed
                trips_query['trips']['start_date'] = new_start_date
                trips_query['trips']['end_date'] = new_end_date
                trips_query['trips']['waypoint']['waypoint_destination'] = new_waypoint_destination
                trips_query['trips']['waypoint']['location']['latitude'] = new_latitude
                trips_query['trips']['waypoint']['location']['longitude'] = new_longitude
                collection_of_trips.save(trips_query)
                print('The changes to the trip has been saved')
                return(trips_query, 200, None)
        else:

            print('Couldnot find the document the user is trying to edit')
            return(None, 404, None)

    # def patch(self):
        # This is essentially the function where we patch resources
        # First things first we need access to the collection


# This is essentially our decorator and what we are doing here is that we are basically self contained blocks of code that we can pass around
def authenticated_request(func):
    def wrapper(*args, **kwargs):
        auth = request.authorization

        if not auth or not validate_auth(auth.username, auth.password):
            return ({'error': 'Basic Auth Required.'}, 401, None)

        return func(*args, **kwargs)

    return wrapper

api.add_resource(User, '/users')
api.add_resource(Trips, '/trips')

@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp
# Encodes our resouces for us


if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
