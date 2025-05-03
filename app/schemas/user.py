from marshmallow import Schema, fields, validates, ValidationError
import json

class UserRegistrationSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.Str(required=True)
    phone_numbers = fields.List(fields.Str(), required=False)
    address = fields.Str(required=True)
    profile_picture = fields.Str(required=False)
    
    @validates('gender')
    def validate_gender(self, value):
        valid_genders = ['Male', 'Female', 'Other']
        if value not in valid_genders:
            raise ValidationError('Gender must be one of: Male, Female, Other')
    
    @validates('confirm_password')
    def validate_confirm_password(self, value, **kwargs):
        if kwargs['data']['password'] != value:
            raise ValidationError('Passwords do not match')

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserProfileSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    date_of_birth = fields.Date()
    gender = fields.Str()
    phone_numbers = fields.Method('get_phone_numbers')
    address = fields.Str()
    profile_picture = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    
    def get_phone_numbers(self, obj):
        if isinstance(obj.phone_numbers, str):
            return json.loads(obj.phone_numbers)
        return obj.phone_numbers