
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse


def main():
    print("Hello from api-activity!")


if __name__ == "__main__":
    main()


# Create the flask app
app = Flask(__name__)

# Create the API object
api = Api(app)

# Create the "hello" resource
class Hello(Resource):
    # Get is a special mdthod for a resource
    def get(self):
        return jsonify({"message": "Hello World!"})
    
class Square(Resource):
    def get(self, num):
        return jsonify({'Shape': __class__.__name__,
                        'Area': num*num})


class Echo(Resource):
    # Use RequestsParser to parse the arguments from the request
    # don't reinvent the Wheel, we could write a parser ourselves but why not
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('arg1', type=str, location='args')
        parser.add_argument('arg2', type=str, location='args')

        arguments = parser.parse_args()

        # Return the arguments as JSON
        return jsonify(arguments)


api.add_resource(Hello, '/')
api.add_resource(Square, "/square/<int:num>")
api.add_resource(Echo, "/echo")



if __name__ == "__main__":
    app.run(debug=True)